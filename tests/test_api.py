"""API-level tests using FastAPI's TestClient (offline, no API key required)."""
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health():
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok"}


def test_analyze_invoice_endpoint():
    resp = client.post(
        "/analyze",
        json={"text": "INVOICE\nTotal due: €1,240.00\nVAT included"},
    )
    assert resp.status_code == 200
    body = resp.json()
    assert body["document_type"] == "invoice"
    assert any(e["label"] == "AMOUNT" for e in body["entities"])


def test_analyze_without_summary():
    resp = client.post(
        "/analyze",
        json={"text": "First sentence. Second sentence.", "summarize": False},
    )
    assert resp.status_code == 200
    assert resp.json()["summary"] is None


def test_analyze_rejects_empty_text():
    resp = client.post("/analyze", json={"text": ""})
    assert resp.status_code == 422
