from unittest.mock import MagicMock, patch
import pytest
from fastapi.testclient import TestClient


@pytest.fixture(scope="module")
def client():
    """
    Test client fixture with a mocked transformer pipeline.
    Prevents downloading heavy model weights during unit tests.
    """
    mock_gen = MagicMock()
    mock_gen.return_value = [{"generated_text": "cloud infrastructure automated inference test"}]

    with patch("transformers.pipeline", return_value=mock_gen):
        import serve
        # Ensure generator references the mock even if imported earlier
        serve.generator = mock_gen
        with TestClient(serve.app) as test_client:
            yield test_client


def test_healthz(client: TestClient):
    """Liveness probe test (/healthz)."""
    response = client.get("/healthz")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_metrics(client: TestClient):
    """Prometheus metrics endpoint test (/metrics)."""
    response = client.get("/metrics")
    assert response.status_code == 200
    assert "text/plain" in response.headers.get("content-type", "")
    assert "inferencia_requests_total" in response.text
    assert "inferencia_latency_seconds" in response.text


def test_predict_success(client: TestClient):
    """Inference endpoint test (/predict) with valid payload."""
    payload = {
        "prompt": "Continuous integration is",
        "max_new_tokens": 15,
    }
    response = client.post("/predict", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["model"] == "distilgpt2"
    assert "output" in data
    assert len(data["output"]) > 0


def test_predict_validation_error(client: TestClient):
    """Inference endpoint test (/predict) with invalid payload (missing prompt)."""
    invalid_payload = {
        "max_new_tokens": 10,
    }
    response = client.post("/predict", json=invalid_payload)
    assert response.status_code == 422  # Pydantic validation error

