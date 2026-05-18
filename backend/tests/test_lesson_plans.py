def lesson_plan_payload(**overrides):
    payload = {
        "title": "Introducao ao OSPF",
        "objective": "Entender o funcionamento basico do OSPF",
        "summary": "Aula introdutoria sobre roteamento dinamico usando OSPF.",
        "planned_date": "2026-05-20",
        "discipline": "Redes",
        "contents": ["Roteamento dinamico", "Areas OSPF"],
        "support_resources": ["Slides", "Laboratorio"],
        "tags": ["OSPF", "Redes"],
    }
    payload.update(overrides)
    return payload


def create_lesson_plan(client, **overrides):
    response = client.post("/lesson-plans", json=lesson_plan_payload(**overrides))
    assert response.status_code == 201
    return response.get_json()


def test_create_valid_lesson_plan(client):
    data = create_lesson_plan(client)

    assert data["id"]
    assert data["title"] == "Introducao ao OSPF"
    assert data["discipline"] == "Redes"
    assert data["contents"] == ["Roteamento dinamico", "Areas OSPF"]
    assert data["support_resources"] == ["Slides", "Laboratorio"]
    assert data["tags"] == ["OSPF", "Redes"]


def test_create_invalid_lesson_plan_returns_400(client):
    payload = lesson_plan_payload()
    payload.pop("title")

    response = client.post("/lesson-plans", json=payload)

    assert response.status_code == 400
    assert response.get_json()["error"] == "Validation error"


def test_create_lesson_plan_with_blank_title_returns_400(client):
    response = client.post("/lesson-plans", json=lesson_plan_payload(title=" "))

    assert response.status_code == 400


def test_list_lesson_plans_with_pagination(client):
    create_lesson_plan(client, title="Introducao ao OSPF")
    create_lesson_plan(client, title="Introducao ao BGP")

    response = client.get("/lesson-plans?page=1&per_page=10")
    data = response.get_json()

    assert response.status_code == 200
    assert "items" in data
    assert "pagination" in data
    assert data["pagination"]["page"] == 1
    assert data["pagination"]["per_page"] == 10
    assert data["pagination"]["total_items"] >= 2


def test_get_lesson_plan_by_id(client):
    created = create_lesson_plan(client)

    response = client.get(f"/lesson-plans/{created['id']}")

    assert response.status_code == 200
    assert response.get_json()["id"] == created["id"]


def test_get_missing_lesson_plan_returns_404(client):
    response = client.get("/lesson-plans/999999")

    assert response.status_code == 404
    assert response.get_json()["error"] == "Lesson plan not found"


def test_update_lesson_plan(client):
    created = create_lesson_plan(client)

    response = client.put(
        f"/lesson-plans/{created['id']}",
        json={"title": "OSPF Avancado", "discipline": "Infraestrutura"},
    )
    data = response.get_json()

    assert response.status_code == 200
    assert data["title"] == "OSPF Avancado"
    assert data["discipline"] == "Infraestrutura"


def test_delete_lesson_plan(client):
    created = create_lesson_plan(client)

    delete_response = client.delete(f"/lesson-plans/{created['id']}")
    get_response = client.get(f"/lesson-plans/{created['id']}")

    assert delete_response.status_code in {200, 204}
    assert get_response.status_code == 404


def test_search_filter(client):
    ospf = create_lesson_plan(client, title="Introducao ao OSPF")
    create_lesson_plan(client, title="Introducao ao BGP", tags=["BGP"])

    response = client.get("/lesson-plans?search=OSPF")
    items = response.get_json()["items"]

    assert response.status_code == 200
    assert any(item["id"] == ospf["id"] for item in items)
    assert all("OSPF" in item["title"] for item in items)


def test_discipline_filter(client):
    redes = create_lesson_plan(client, discipline="Redes")
    create_lesson_plan(client, title="Plano de Python", discipline="Programacao")

    response = client.get("/lesson-plans?discipline=Redes")
    items = response.get_json()["items"]

    assert response.status_code == 200
    assert any(item["id"] == redes["id"] for item in items)
    assert all(item["discipline"] == "Redes" for item in items)


def test_tag_filter(client):
    ospf = create_lesson_plan(client, tags=["OSPF", "Redes"])
    create_lesson_plan(client, title="Plano de BGP", tags=["BGP"])

    response = client.get("/lesson-plans?tag=OSPF")
    items = response.get_json()["items"]

    assert response.status_code == 200
    assert any(item["id"] == ospf["id"] for item in items)
    assert all("OSPF" in item["tags"] for item in items)


def test_sort_by_title_does_not_break_listing(client):
    create_lesson_plan(client, title="B Plano")
    create_lesson_plan(client, title="A Plano")

    response = client.get("/lesson-plans?sort_by=title&order=asc")
    data = response.get_json()

    assert response.status_code == 200
    assert "items" in data
    assert "pagination" in data
    assert len(data["items"]) >= 2
