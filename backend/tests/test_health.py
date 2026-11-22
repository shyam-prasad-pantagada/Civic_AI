"""Civic_AI Health and System Diagnostics Tests."""

from fastapi.testclient import TestClient


def test_health_check(client: TestClient) -> None:
    """Test that GET /health returns 200 and exact JSON payload."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data == {
        "status": "ok",
        "app": "Civic_AI",
        "version": "0.1.0",
    }


def test_api_routes_mounted(client: TestClient) -> None:
    """Test that core API routes are mounted and responsive."""
    # Test states coverage endpoint
    states_resp = client.get("/api/states?lang=en")
    assert states_resp.status_code == 200
    states_data = states_resp.json()
    assert "states" in states_data
    assert states_data["total_states"] == 36
    assert "DL" in states_data["pilot_states"]

    # Test unsupported language rejection
    unsupported_resp = client.get("/api/states?lang=unsupported_code")
    assert unsupported_resp.status_code == 400
