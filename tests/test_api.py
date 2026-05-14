from fastapi.testclient import TestClient

from fasikl_assistant.api import app

client = TestClient(app)


def test_health_endpoint_reports_ready():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_analyze_endpoint_returns_patient_assistant_result():
    response = client.post(
        "/analyze",
        json={
            "id": "C004",
            "transcript": "I cannot log into the portal.",
            "session_id": "api-test",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["category"] == "account_access"
    assert data["action"] == "auto_reply"
    assert data["portal_link"]["path"] == "/login/help"


def test_run_samples_endpoint_processes_goal_examples():
    response = client.post("/samples/run")

    assert response.status_code == 200
    data = response.json()
    assert len(data["results"]) == 10
    assert {item["id"] for item in data["results"]} == {
        "C001",
        "C002",
        "C003",
        "C004",
        "C005",
        "C006",
        "C007",
        "C008",
        "C009",
        "C010",
    }
