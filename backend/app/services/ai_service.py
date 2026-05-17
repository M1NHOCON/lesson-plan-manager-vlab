import json
import logging
import os
import re

from openai import OpenAI

from app.utils.logger import get_logger


logger = get_logger(__name__)
logging.getLogger("httpx").setLevel(logging.WARNING)

MOCK_API_KEYS = {None, "", "your_api_key_here"}
OPENAI_MODEL = "gpt-4o-mini"
OPENAI_TIMEOUT_SECONDS = 20


def generate_recommendations(payload, api_key=None, provider=None):
    logger.info("AI recommendation requested")
    api_key = api_key or os.getenv("LLM_API_KEY")
    provider = provider or os.getenv("LLM_PROVIDER")

    if _should_use_mock(api_key, provider):
        logger.info("Using mock AI recommendations")
        return _mock_recommendations(payload)

    try:
        logger.info("OpenAI recommendation request started")
        result = _call_openai(payload, api_key)
        logger.info("OpenAI recommendation request succeeded")
        return {**result, "source": "openai"}
    except Exception as error:
        logger.exception("OpenAI recommendation request failed: %s", error)
        return _fallback_with_warning(payload)


def _should_use_mock(api_key, provider):
    normalized_api_key = (api_key or "").strip()
    normalized_provider = (provider or "").strip().lower()

    if normalized_api_key in MOCK_API_KEYS:
        logger.info("Fallback activated: missing OpenAI API key")
        return True

    if normalized_provider != "openai":
        logger.info("Fallback activated: provider is not openai")
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
    client = OpenAI(api_key=os.getenv("LLM_API_KEY") or api_key)
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
    parsed_content = json.loads(content)
    return _validate_ai_response(parsed_content)


def _validate_ai_response(result):
    if not isinstance(result, dict):
        raise ValueError("OpenAI response must be a JSON object")

    missing_fields = [
        field
        for field in ("contents", "related_topics", "tags")
        if field not in result
    ]
    if missing_fields:
        raise ValueError(f"OpenAI response missing fields: {missing_fields}")

    contents = _string_list(result.get("contents"))
    related_topics = _string_list(result.get("related_topics"))
    tags = _string_list(result.get("tags"))[:3]

    if not contents:
        raise ValueError("OpenAI response contents must be a non-empty string list")
    if not related_topics:
        raise ValueError("OpenAI response related_topics must be a non-empty string list")
    if len(tags) != 3:
        raise ValueError("OpenAI response tags must contain exactly 3 strings")

    return {
        "contents": contents,
        "related_topics": related_topics,
        "tags": tags,
    }


def _fallback_with_warning(payload):
    logger.info("Fallback mock activated")
    fallback = _mock_recommendations(payload)
    fallback["source"] = "mock"
    fallback["warning"] = "OpenAI failed; mock recommendations returned"
    return fallback


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
