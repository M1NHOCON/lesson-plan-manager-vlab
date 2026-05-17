import json
import re
import urllib.error
import urllib.request

from app.utils.logger import get_logger


logger = get_logger(__name__)

MOCK_API_KEYS = {None, "", "your_api_key_here"}


def generate_recommendations(payload, api_key=None, provider=None):
    logger.info("AI recommendation requested")

    if not _has_valid_api_key(api_key):
        logger.info("Using mock AI recommendations")
        return _mock_recommendations(payload)

    try:
        logger.info("Calling real AI provider: %s", provider or "openai")
        result = _call_ai_provider(payload, api_key, provider)
        return _normalize_ai_response(result)
    except Exception as error:
        logger.exception("AI provider failed: %s", error)
        fallback = _mock_recommendations(payload)
        fallback["source"] = "mock"
        fallback["warning"] = "AI provider failed; mock recommendations returned"
        return fallback


def _has_valid_api_key(api_key):
    return api_key not in MOCK_API_KEYS


def _build_prompt(payload):
    return (
        "Voce e um Assistente Pedagogico. Gere sugestoes para um plano de aula "
        "com conteudos complementares, topicos relacionados e exatamente 3 tags. "
        "Responda exclusivamente com JSON valido, sem markdown, no formato: "
        '{"contents":["..."],"related_topics":["..."],"tags":["...","...","..."]}\n\n'
        f"Titulo: {payload['title']}\n"
        f"Disciplina: {payload['discipline']}\n"
        f"Resumo: {payload['summary']}"
    )


def _call_ai_provider(payload, api_key, provider):
    normalized_provider = (provider or "openai").strip().lower()
    prompt = _build_prompt(payload)

    if normalized_provider in {"gemini", "google", "google_gemini"}:
        return _call_gemini(prompt, api_key)

    return _call_openai(prompt, api_key)


def _call_openai(prompt, api_key):
    body = {
        "model": "gpt-4o-mini",
        "messages": [
            {
                "role": "system",
                "content": "Voce retorna apenas JSON valido, sem markdown.",
            },
            {"role": "user", "content": prompt},
        ],
        "temperature": 0.4,
    }

    data = _post_json(
        "https://api.openai.com/v1/chat/completions",
        body,
        {"Authorization": f"Bearer {api_key}"},
    )
    content = data["choices"][0]["message"]["content"]
    return _parse_json_content(content)


def _call_gemini(prompt, api_key):
    body = {
        "contents": [
            {
                "parts": [
                    {
                        "text": prompt,
                    }
                ]
            }
        ],
        "generationConfig": {
            "temperature": 0.4,
            "responseMimeType": "application/json",
        },
    }

    data = _post_json(
        f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}",
        body,
        {},
    )
    content = data["candidates"][0]["content"]["parts"][0]["text"]
    return _parse_json_content(content)


def _post_json(url, body, headers):
    request = urllib.request.Request(
        url,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Content-Type": "application/json",
            **headers,
        },
        method="POST",
    )

    try:
        with urllib.request.urlopen(request, timeout=20) as response:
            return json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as error:
        details = error.read().decode("utf-8", errors="ignore")
        raise RuntimeError(f"AI provider returned HTTP {error.code}: {details}") from error
    except urllib.error.URLError as error:
        raise RuntimeError(f"AI provider request failed: {error.reason}") from error


def _parse_json_content(content):
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", content, flags=re.DOTALL)
        if not match:
            raise
        return json.loads(match.group(0))


def _normalize_ai_response(result):
    tags = _string_list(result.get("tags"))[:3]
    while len(tags) < 3:
        tags.append("Educacao")

    return {
        "contents": _string_list(result.get("contents")),
        "related_topics": _string_list(result.get("related_topics")),
        "tags": tags,
    }


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
