def test_docs_route_is_available(client):
    response = client.get("/docs/")

    assert response.status_code in {200, 308}


def test_apispec_contains_main_routes(client):
    response = client.get("/apispec.json")
    data = response.get_json()
    paths = data["paths"]

    assert response.status_code == 200
    assert "/health" in paths
    assert "/lesson-plans" in paths
    assert "/ai/recommendations" in paths
