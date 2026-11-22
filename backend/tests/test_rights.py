"""Tests for Civic_AI Citizen Rights RAG Service."""

import pytest
from fastapi.testclient import TestClient


def test_rights_query_tenancy_eviction_citation(client: TestClient):
    """Test tenancy question returns Model Tenancy Act citation."""
    response = client.post(
        "/api/rights",
        json={
            "question": "Can my landlord evict me without notice or cut my water supply?",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["has_official_source"] is True
    assert len(data["citations"]) > 0
    citation = data["citations"][0]
    assert "Tenancy" in citation["act_name"]
    assert "Section" in citation["section"]
    assert citation["url"].startswith("http")
    assert len(data["your_rights"]) > 0
    assert len(data["where_to_complain_or_get_free_help"]) > 0
    assert any("15100" in h or "NALSA" in h for h in data["where_to_complain_or_get_free_help"])


def test_rights_query_consumer_refund_citation(client: TestClient):
    """Test consumer dispute returns Consumer Protection Act citation."""
    response = client.post(
        "/api/rights",
        json={
            "question": "Can a company refuse refund for defective goods?",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert data["has_official_source"] is True
    assert len(data["citations"]) > 0
    assert "Consumer Protection" in data["citations"][0]["act_name"]


def test_rights_query_no_source_fallback(client: TestClient):
    """Test unrelated non-legal question triggers strict no-source fallback and legal aid referral."""
    response = client.post(
        "/api/rights",
        json={
            "question": "What is the best recipe to make paneer butter masala?",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()

    # Must abstain and cite no official source
    assert data["has_official_source"] is False
    assert len(data["citations"]) == 0
    assert any("could not locate" in r.lower() for r in data["your_rights"])
    # Must refer to NALSA free legal aid
    assert any("15100" in h or "NALSA" in h for h in data["where_to_complain_or_get_free_help"])
