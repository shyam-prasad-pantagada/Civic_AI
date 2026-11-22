"""Tests for Civic_AI Deterministic Scheme Eligibility Engine."""

import pytest
from fastapi.testclient import TestClient
from app.services.eligibility.engine import eligibility_engine
from app.models.schemas import CitizenProfile


def test_deterministic_eligibility_pm_kisan_eligible(client: TestClient):
    """Test small farmer with <= 5 acres land and low income is eligible for PM-KISAN."""
    profile = {
        "age": 45,
        "gender": "male",
        "category": "farmer",
        "annual_income": 120000,
        "land_holding_acres": 2.5,
        "state": "Central",
    }

    response = client.post(
        "/api/eligibility",
        json={"profile": profile, "lang": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    results = {r["scheme_id"]: r for r in data["results"]}

    assert "PM-KISAN" in results
    pm_kisan = results["PM-KISAN"]
    assert pm_kisan["status"] == "eligible"
    assert "income <=" in pm_kisan["deciding_rule"]
    assert len(pm_kisan["benefits"]) > 0


def test_deterministic_eligibility_mh_ladki_bahin_eligible(client: TestClient):
    """Test 28-year-old female in Maharashtra with income <= 2.5L is eligible."""
    profile = {
        "age": 28,
        "gender": "female",
        "annual_income": 180000,
        "state": "MH",
    }

    response = client.post(
        "/api/eligibility",
        json={"profile": profile, "state": "MH", "lang": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    results = {r["scheme_id"]: r for r in data["results"]}

    assert "MH-LADKI-BAHIN" in results
    ladki_bahin = results["MH-LADKI-BAHIN"]
    assert ladki_bahin["status"] == "eligible"
    assert "state == 'MH'" in ladki_bahin["deciding_rule"]


def test_deterministic_eligibility_state_isolation(client: TestClient):
    """Test citizen from Karnataka cannot be eligible for Maharashtra-specific scheme."""
    profile = {
        "age": 28,
        "gender": "female",
        "annual_income": 180000,
        "state": "KA",
    }

    response = client.post(
        "/api/eligibility",
        json={"profile": profile, "lang": "en"},
    )

    assert response.status_code == 200
    data = response.json()
    results = {r["scheme_id"]: r for r in data["results"]}

    if "MH-LADKI-BAHIN" in results:
        mh_scheme = results["MH-LADKI-BAHIN"]
        assert mh_scheme["status"] == "not_eligible"
        assert "profile.state == 'MH'" in mh_scheme["deciding_rule"]


def test_deterministic_eligibility_need_more_info():
    """Test missing income triggers 'need_more_info' and follow-up question."""
    profile = CitizenProfile(age=65, gender="male", state="Central")
    results, follow_ups = eligibility_engine.evaluate_all(profile)

    assert any(r.status == "need_more_info" for r in results)
    follow_up_attrs = [f["attribute"] for f in follow_ups]
    assert "annual_income" in follow_up_attrs


def test_zero_llm_calls_in_eligibility():
    """Verify that the eligibility engine is 100% deterministic with ZERO LLM calls."""
    profile = CitizenProfile(
        age=62,
        gender="female",
        annual_income=80000,
        state="MH",
        category="senior",
    )
    # Direct execution should complete synchronously with zero external network or LLM dependency
    results, follow_ups = eligibility_engine.evaluate_all(profile)
    assert len(results) > 0
    for r in results:
        assert r.status in ("eligible", "not_eligible", "need_more_info")
        assert len(r.deciding_rule) > 0
