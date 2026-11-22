"""Tests for Civic_AI Notice and Document Explainer API."""

import pytest
from fastapi.testclient import TestClient


def test_explain_text_notice_success(client: TestClient):
    """Test explaining a raw text government circular."""
    sample_notice = (
        "GOVERNMENT OF INDIA - MINISTRY OF CONSUMER AFFAIRS\n"
        "NOTIFICATION NO. 14/2026\n"
        "All retail merchants must display digital QR payment codes and price lists prominently. "
        "The mandatory compliance deadline is 31st December 2026. "
        "Required documents include Trade License and GSTIN registration certificate. "
        "Merchants failing to comply before 31-12-2026 shall be liable to penalties under Section 18."
    )

    response = client.post(
        "/api/explain",
        json={
            "text": sample_notice,
            "document_type": "circular",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()

    assert "plain_summary" in data
    assert len(data["plain_summary"]) > 20
    assert "who_is_affected" in data
    assert isinstance(data["key_points"], list)
    assert len(data["key_points"]) > 0
    assert isinstance(data["actions_for_citizen"], list)
    assert len(data["actions_for_citizen"]) > 0
    assert data["lang"] == "en"
    assert data["source_url"] is not None


def test_explain_empty_text_fails(client: TestClient):
    """Test that empty payload returns 400 Bad Request."""
    response = client.post(
        "/api/explain",
        json={"text": "   ", "lang": "en"},
    )
    assert response.status_code == 400


def test_explain_unsupported_language_fails(client: TestClient):
    """Test that unsupported language code returns clean 400 error."""
    response = client.post(
        "/api/explain",
        json={"text": "Government notice sample text", "lang": "unsupported_xyz"},
    )
    assert response.status_code == 400
    assert "not currently enabled" in response.json()["detail"]
