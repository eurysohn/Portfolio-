from fastapi.testclient import TestClient

from api.main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"

def test_query_endpoint():
    response = client.post("/query", json={"query": "What is OTIF?", "top_k": 3})
    assert response.status_code == 200
    assert "answer" in response.json()
    assert "OTIF" in response.json()["answer"]

def test_metrics_endpoint():
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "scm_api_requests_total" in response.text
