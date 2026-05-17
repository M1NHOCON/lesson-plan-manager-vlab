def ai_payload(**overrides):
    payload = {
        "title": "Introducao ao OSPF",
        "discipline": "Redes de Computadores",
        "summary": "Aula introdutoria sobre roteamento dinamico usando OSPF.",
    }
    payload.update(overrides)
    return payload


def test_ai_recommendations_with_mock(client):
    response = client.post("/ai/recommendations", json=ai_payload())
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "mock"
    assert isinstance(data["contents"], list)
    assert isinstance(data["related_topics"], list)
    assert isinstance(data["tags"], list)
    assert len(data["tags"]) == 3


def test_ai_recommendations_invalid_payload_returns_400(client):
    response = client.post("/ai/recommendations", json=ai_payload(title=" "))

    assert response.status_code == 400
    assert response.get_json()["error"] == "Validation error"


def test_ai_recommendations_gemini_without_key_uses_mock(app, client):
    app.config["LLM_PROVIDER"] = "gemini"
    app.config["LLM_API_KEY"] = "your_api_key_here"

    response = client.post("/ai/recommendations", json=ai_payload())
    data = response.get_json()

    assert response.status_code == 200
    assert data["source"] == "mock"
