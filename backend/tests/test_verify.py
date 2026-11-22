"""Tests for Civic_AI Live Verification and Domain Allow-list Service."""

import pytest
from fastapi.testclient import TestClient
from app.services.verify import verification_service


def test_allowed_domains_whitelisting():
    """Verify that only authorized official government domains are allowed."""
    assert verification_service.is_domain_allowed("https://pmkisan.gov.in") is True
    assert verification_service.is_domain_allowed("https://indiacode.nic.in/handle/123") is True
    assert verification_service.is_domain_allowed("https://egazette.gov.in") is True
    assert verification_service.is_domain_allowed("https://random-scam-site.com") is False
    assert verification_service.is_domain_allowed("https://commercial-blog.org/pmkisan") is False


def test_verify_endpoint_official_source(client: TestClient):
    """Test verify endpoint with official .gov.in source returns 'Verified today' badge."""
    response = client.post(
        "/api/verify",
        json={
            "claim_or_circular_title": "PM-KISAN 17th Installment Release",
            "source_url": "https://pmkisan.gov.in",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["badge"] == "Verified today"
    assert "pmkisan.gov.in" in data["source_url"]
    assert data["last_verified"] is not None


def test_verify_endpoint_unauthorized_domain(client: TestClient):
    """Test verify endpoint with non-government domain returns 'Could not verify'."""
    response = client.post(
        "/api/verify",
        json={
            "claim_or_circular_title": "Unverified Telegram circular",
            "source_url": "https://unverified-thirdparty-site.net/fake.pdf",
            "lang": "en",
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["badge"] == "Could not verify"
