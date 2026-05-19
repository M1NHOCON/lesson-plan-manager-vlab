import json
import logging
import os
import re
import time

from google import genai
from google.genai import types
from openai import OpenAI

from app.utils.logger import get_logger


logger = get_logger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

MOCK_API_KEYS = {None, "", "your_api_key_here"}
OPENAI_MODEL = "gpt-4o-mini"
GEMINI_MODEL = "gemini-2.5-flash"
OPENAI_TIMEOUT_SECONDS = 20
GEMINI_TIMEOUT_SECONDS = 20
SUPPORTED_PROVIDERS = {"openai", "gemini"}


def generate_recommendations(payload, api_key=None, provider=None):
    title = payload.get("title")
    discipline = payload.get("discipline")
    provider = _normalize_provider(provider or os.getenv("LLM_PROVIDER"))
    api_key = _resolve_api_key(api_key, provider)
    provider_label = provider or "mock"
    logger.info(
        'AI Request Started: Title="%s", Discipline="%s", Provider="%s"',
        title,
        discipline,
        provider_label,
    )

    mock_reason = _mock_reason(api_key, provider)
    if mock_reason:
        logger.info(
            'AI Mock Used: Title="%s", Discipline="%s", Reason="%s", Source="mock"',
            title,
            discipline,
            mock_reason,
        )
        return _mock_recommendations(payload)

    started_at = time.perf_counter()
    try:
        result, token_usage = _call_provider(payload, api_key, provider)
        latency = _format_latency(started_at)
        if token_usage is None:
            logger.info(
                'AI Request: Title="%s", Discipline="%s", Provider="%s", '
                'Source="%s", Latency=%ss',
                title,
                discipline,
                provider,
                provider,
                latency,
            )
        else:
            logger.info(
                'AI Request: Title="%s", Discipline="%s", Provider="%s", '
                'Source="%s", TokenUsage=%s, Latency=%ss',
                title,
                discipline,
                provider,
                provider,
                token_usage,
                latency,
            )
        return {**result, "source": provider}
    except Exception as error:
        latency = _format_latency(started_at)
        reason = _short_error(error)
        logger.warning(
            'AI Fallback: Provider="%s", Reason="%s", Source="mock", Latency=%ss',
            provider,
            reason,
            latency,
        )
        return _fallback_with_warning(payload, provider)


def _normalize_provider(provider):
    return (provider or "").strip().lower()


def _resolve_api_key(api_key, provider):
    if provider == "gemini":
        gemini_api_key = os.getenv("GEMINI_API_KEY")
        if _is_valid_api_key(gemini_api_key):
            return gemini_api_key
        return api_key or os.getenv("LLM_API_KEY")

    if _is_valid_api_key(api_key):
        return api_key

    return os.getenv("LLM_API_KEY")


def _is_valid_api_key(api_key):
    return (api_key or "").strip() not in MOCK_API_KEYS


def _mock_reason(api_key, provider):
    normalized_api_key = (api_key or "").strip()

    if normalized_api_key in MOCK_API_KEYS:
        return "missing or placeholder API key"

    if provider not in SUPPORTED_PROVIDERS:
        return "unsupported provider"

    return None


def _build_prompt(payload):
    return (
        "Voce e um Assistente Pedagogico especializado em planejamento de aulas. "
        "Com base no titulo, disciplina e resumo abaixo, gere sugestoes objetivas "
        "para enriquecer o plano de aula. A resposta deve conter conteudos "
        "complementares, topicos relacionados e exatamente 3 tags. "
        "Responda exclusivamente com JSON valido, sem markdown, sem comentarios e "
        "sem explicacoes adicionais. Use obrigatoriamente este formato: "
        '{"contents":["..."],"related_topics":["..."],"tags":["...","...","..."]}\n\n'
        f"Titulo: {payload['title']}\n"
        f"Disciplina: {payload['discipline']}\n"
        f"Resumo: {payload['summary']}"
    )


def _call_openai(payload, api_key):
    client = OpenAI(api_key=api_key)
    prompt = _build_prompt(payload)

    response = client.chat.completions.create(
        model=OPENAI_MODEL,
        messages=[
            {
                "role": "system",
                "content": (
                    "Voce e um Assistente Pedagogico. Retorne apenas JSON valido, "
                    "sem markdown e sem explicacoes."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature=0.4,
        response_format={"type": "json_object"},
        timeout=OPENAI_TIMEOUT_SECONDS,
    )

    content = response.choices[0].message.content
    parsed_content = _parse_ai_json_response(content)
    token_usage = _extract_openai_token_usage(response)
    return _validate_ai_response(parsed_content), token_usage


def _call_provider(payload, api_key, provider):
    if provider == "gemini":
        return _call_gemini(payload, api_key)

    return _call_openai(payload, api_key)


def _call_gemini(payload, api_key):
    client = genai.Client(api_key=api_key)
    prompt = _build_prompt(payload)

    response = client.models.generate_content(
        model=GEMINI_MODEL,
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.4,
            response_mime_type="application/json",
            http_options=types.HttpOptions(timeout=GEMINI_TIMEOUT_SECONDS * 1000),
        ),
    )

    parsed_content = _parse_ai_json_response(response.text)
    token_usage = _extract_gemini_token_usage(response)
    return _validate_ai_response(parsed_content), token_usage


def _parse_ai_json_response(content):
    if not content:
        raise ValueError("AI response content is empty")

    cleaned = content.strip()
    fenced_match = re.search(
        r"```(?:json)?\s*(\{.*?\})\s*```",
        cleaned,
        flags=re.DOTALL | re.IGNORECASE,
    )
    if fenced_match:
        cleaned = fenced_match.group(1).strip()

    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        object_match = re.search(r"\{.*\}", cleaned, flags=re.DOTALL)
        if not object_match:
            raise
        return json.loads(object_match.group(0))


def _validate_ai_response(result):
    if not isinstance(result, dict):
        raise ValueError("AI response must be a JSON object")

    missing_fields = [
        field
        for field in ("contents", "related_topics", "tags")
        if field not in result
    ]
    if missing_fields:
        raise ValueError(f"AI response missing fields: {missing_fields}")

    contents = _required_string_list(result.get("contents"), "contents")
    related_topics = _required_string_list(
        result.get("related_topics"),
        "related_topics",
    )
    tags = _required_string_list(result.get("tags"), "tags")

    if not contents:
        raise ValueError("AI response contents must be a non-empty string list")
    if not related_topics:
        raise ValueError("AI response related_topics must be a non-empty string list")
    if len(tags) != 3:
        raise ValueError("AI response tags must contain exactly 3 strings")

    return {
        "contents": contents,
        "related_topics": related_topics,
        "tags": tags,
    }


def _fallback_with_warning(payload, provider):
    fallback = _mock_recommendations(payload)
    fallback["source"] = "mock"
    fallback["warning"] = f"{_provider_label(provider)} failed; mock recommendations returned"
    return fallback


def _format_latency(started_at):
    return f"{time.perf_counter() - started_at:.2f}"


def _short_error(error):
    message = str(error).strip()
    if not message:
        return error.__class__.__name__

    first_line = message.splitlines()[0].strip()
    return first_line[:160]


def _extract_openai_token_usage(response):
    usage = getattr(response, "usage", None)
    total_tokens = getattr(usage, "total_tokens", None)
    return total_tokens if isinstance(total_tokens, int) else None


def _extract_gemini_token_usage(response):
    metadata = getattr(response, "usage_metadata", None)
    total_tokens = getattr(metadata, "total_token_count", None)
    return total_tokens if isinstance(total_tokens, int) else None


def _provider_label(provider):
    if provider == "openai":
        return "OpenAI"
    if provider == "gemini":
        return "Gemini"
    return "AI provider"


def _mock_recommendations(payload):
    title = payload["title"]
    discipline = payload["discipline"]
    summary = payload["summary"]
    keywords = _extract_keywords(f"{title} {discipline} {summary}")
    main_topic = keywords[0] if keywords else title

    contents = [
        f"Conceitos fundamentais de {main_topic}",
        f"Aplicacoes praticas em {discipline}",
        f"Exemplos guiados sobre {title}",
    ]
    related_topics = [
        f"Fundamentos de {discipline}",
        f"Boas praticas relacionadas a {main_topic}",
        f"Estudos de caso sobre {title}",
    ]
    tags = _build_tags(keywords, discipline)

    return {
        "contents": contents,
        "related_topics": related_topics,
        "tags": tags,
        "source": "mock",
    }


def _extract_keywords(text):
    stopwords = {
        "a",
        "ao",
        "as",
        "com",
        "da",
        "de",
        "do",
        "dos",
        "e",
        "em",
        "introdutoria",
        "introducao",
        "o",
        "os",
        "para",
        "sobre",
        "uma",
        "usando",
    }
    words = re.findall(r"[A-Za-zÀ-ÿ0-9]+", text)
    keywords = []

    for word in words:
        normalized = word.strip()
        if len(normalized) < 3 or normalized.lower() in stopwords:
            continue
        if normalized.lower() not in {item.lower() for item in keywords}:
            keywords.append(normalized)

    return keywords[:5]


def _build_tags(keywords, discipline):
    tags = keywords[:2]
    discipline_tag = discipline.split()[0] if discipline else "Aula"
    tags.append(discipline_tag)

    unique_tags = []
    for tag in tags:
        cleaned = tag.strip()
        if cleaned and cleaned.lower() not in {item.lower() for item in unique_tags}:
            unique_tags.append(cleaned)

    while len(unique_tags) < 3:
        unique_tags.append("Educacao")

    return unique_tags[:3]


def _string_list(value):
    if not isinstance(value, list):
        return []

    return [item.strip() for item in value if isinstance(item, str) and item.strip()]


def _required_string_list(value, field_name):
    if not isinstance(value, list):
        raise ValueError(f"AI response {field_name} must be a list")

    if not all(isinstance(item, str) and item.strip() for item in value):
        raise ValueError(f"AI response {field_name} must contain only non-empty strings")

    return [item.strip() for item in value]
