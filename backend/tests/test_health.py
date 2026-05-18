def test_health_check_returns_ok(client):
    response = client.get("/health")

    assert response.status_code == 200
    data = response.get_json()
    assert data["status"] == "ok"
    assert "Lesson Plan Manager API is running" in data["message"]
