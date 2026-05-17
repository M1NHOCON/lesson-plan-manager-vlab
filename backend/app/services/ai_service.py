import json
import logging
import os
import re

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
    logger.info("AI recommendation requested")
    provider = _normalize_provider(provider or os.getenv("LLM_PROVIDER"))
    api_key = _resolve_api_key(api_key, provider)
    logger.info("AI provider selected: %s", provider or "mock")

    if _should_use_mock(api_key, provider):
        logger.info("Using mock AI recommendations")
        return _mock_recommendations(payload)

    try:
        logger.info("%s recommendation request started", provider.title())
        result = _call_provider(payload, api_key, provider)
        logger.info("%s recommendation request succeeded", provider.title())
        return {**result, "source": provider}
    except Exception as error:
        logger.exception("%s recommendation request failed: %s", provider.title(), error)
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


def _should_use_mock(api_key, provider):
    normalized_api_key = (api_key or "").strip()

    if normalized_api_key in MOCK_API_KEYS:
        logger.info("Fallback activated: missing API key")
        return True

    if provider not in SUPPORTED_PROVIDERS:
        logger.info("Fallback activated: unsupported provider")
        return True

    return False


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
    return _validate_ai_response(parsed_content)


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
    return _validate_ai_response(parsed_content)


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
    logger.info("Fallback mock activated")
    fallback = _mock_recommendations(payload)
    fallback["source"] = "mock"
    fallback["warning"] = f"{_provider_label(provider)} failed; mock recommendations returned"
    return fallback


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
