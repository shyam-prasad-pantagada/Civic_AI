"""Tests for Civic_AI Platform Statistics Endpoint."""

from fastapi.testclient import TestClient


def test_stats_endpoint_returns_live_counts(client: TestClient):
    """Verify /api/stats returns factual, calculated scheme and rights counts."""
    response = client.get("/api/stats")
    assert response.status_code == 200
    data = response.json()

    assert "total_schemes" in data
    assert data["total_schemes"] >= 36  # Covers at least all 36 states/UTs + central
    assert "schemes_per_state" in data
    assert isinstance(data["schemes_per_state"], dict)
    assert data["states_covered_count"] == 36
    assert data["states_count"] == 28
    assert data["uts_count"] == 8
    assert data["rights_topics_count"] >= 7
    assert "last_synced" in data
    assert data["deterministic_engine"] is True
