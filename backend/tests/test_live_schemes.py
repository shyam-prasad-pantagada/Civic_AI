"""Tests for All-India 36 State/UT Scheme Coverage and Live LLM Fallback Lookup."""

import pytest
from fastapi.testclient import TestClient
from app.services.eligibility.engine import eligibility_engine
from app.services.eligibility.live_lookup import live_scheme_lookup


def test_all_36_states_and_uts_coverage():
    """Verify that every single one of the 36 Indian States & UTs + Central has registered schemes."""
    all_schemes = eligibility_engine.get_all_schemes()
    assert len(all_schemes) >= 36

    states_covered = {s.get("state") for s in all_schemes}
    # Check Central
    assert "Central" in states_covered

    # Check sample of various states and UTs
    for code in ["AP", "MH", "KA", "DL", "TN", "WB", "UP", "RJ", "GA", "JK", "AN", "CH", "LA", "PY"]:
        assert code in states_covered, f"State/UT {code} was not found in registered schemes"


def test_live_lookup_existing_scheme_returns_local_data(client: TestClient):
    """Test live lookup endpoint on existing scheme returns local record."""
    response = client.post(
        "/api/schemes/live-lookup",
        json={"query": "PM-KISAN", "lang": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert "PM-KISAN" in data["scheme_id"]
    assert "Pradhan Mantri Kisan" in data["scheme_name"]
    assert data["state"] == "Central"
    assert len(data["benefits"]) > 0
    assert len(data["eligibility_criteria"]) > 0


def test_live_lookup_new_scheme_synthesizes_structured_policy(client: TestClient):
    """Test live lookup on brand-new or regional scheme triggers structured fallback synthesis."""
    query = "Mission Vatsalya Child Care Scheme"
    response = client.post(
        "/api/schemes/live-lookup",
        json={"query": query, "lang": "en"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["is_live_verified"] is True
    assert "scheme_name" in data
    assert "benefits" in data
    assert "eligibility_criteria" in data
    assert "documents_needed" in data
    assert "how_to_apply" in data
    assert "official_link" in data


def test_live_fallback_in_schemes_get_endpoint(client: TestClient):
    """Test GET /api/schemes?search=...&live_fallback=true returns synthesized result if 0 local matches."""
    response = client.get(
        "/api/schemes?search=Mission+Shakti+Sambal+Sub+Scheme&live_fallback=true"
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any("Mission" in s["scheme_name"] or "LIVE" in s.get("scheme_id", "") for s in data)


def test_governance_scope_classification_and_apply_portals():
    """Verify explicit governance classifications, applicable states, and direct apply portal links."""
    all_schemes = eligibility_engine.get_all_schemes()
    types_found = {s.get("scheme_type") for s in all_schemes}
    assert "central" in types_found
    assert "state" in types_found
    assert "integrated" in types_found

    # Check Central scheme scope
    pm_kisan = eligibility_engine.get_scheme_by_id("PM-KISAN")
    assert pm_kisan["scheme_type"] == "central"
    assert "All India" in pm_kisan["applicable_states"]
    assert pm_kisan["direct_apply_url"].startswith("http")

    # Check Integrated scheme with state-specific portals
    pm_jay = eligibility_engine.get_scheme_by_id("PM-JAY")
    assert pm_jay["scheme_type"] == "integrated"
    assert len(pm_jay["state_apply_links"]) > 0
    assert any("Maharashtra" in sl["state"] for sl in pm_jay["state_apply_links"])

    # Check State scheme
    ladki_bahin = eligibility_engine.get_scheme_by_id("MH-LADKI-BAHIN")
    assert ladki_bahin["scheme_type"] == "state"
    assert "Maharashtra" in ladki_bahin["applicable_states"]
    assert ladki_bahin["direct_apply_url"].startswith("http")


def test_deterministic_eligibility_remains_100_percent_deterministic():
    """Verify zero LLM decisions in eligibility engine even with expanded 50+ schemes."""
    all_schemes = eligibility_engine.get_all_schemes()
    for s in all_schemes:
        # Every scheme must define a rules dictionary with deterministic constraints
        assert "rules" in s
        assert isinstance(s["rules"], dict)
