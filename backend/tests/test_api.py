from fastapi.testclient import TestClient

from hr_assistant_backend.main import app

client = TestClient(app)


def test_health_endpoint() -> None:
    response = client.get("/api/v1/health")

    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_assets_endpoint_filters_available_items() -> None:
    response = client.get("/api/v1/assets", params={"category": "모니터"})

    assert response.status_code == 200
    payload = response.json()
    assert len(payload["items"]) == 2
    assert all(item["status"] == "대여 가능" for item in payload["items"])


def test_chat_endpoint_returns_citations() -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"user_id": "emp-1001", "message": "대여 가능한 모니터 알려줘"},
    )

    assert response.status_code == 200
    payload = response.json()
    assert "모니터" in payload["answer"]
    assert len(payload["citations"]) >= 1
