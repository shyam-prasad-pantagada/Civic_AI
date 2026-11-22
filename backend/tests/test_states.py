"""Tests for Civic_AI State Registry and Coverage API."""

import pytest
from fastapi.testclient import TestClient


def test_states_endpoint_returns_36_states_and_uts(client: TestClient):
    """Verify that all 36 Indian states and union territories are listed."""
    response = client.get("/api/states")
    assert response.status_code == 200
    data = response.json()

    assert data["total_states"] == 36
    assert len(data["states"]) == 36

    # Verify pilot states DL, MH, KA are flagged
    pilot_codes = data["pilot_states"]
    assert "DL" in pilot_codes
    assert "MH" in pilot_codes
    assert "KA" in pilot_codes

    state_dict = {s["code"]: s for s in data["states"]}
    assert "DL" in state_dict
    assert "MH" in state_dict
    assert "KA" in state_dict
    assert state_dict["MH"]["tier"] == 1
    assert state_dict["MH"]["status"] == "verified"

    # Verify exactly 28 States and 8 Union Territories
    indian_states = {"AP", "AR", "AS", "BR", "CG", "GA", "GJ", "HR", "HP", "JH", "KA", "KL", "MP", "MH", "MN", "ML", "MZ", "NL", "OD", "PB", "RJ", "SK", "TN", "TS", "TR", "UP", "UK", "WB"}
    indian_uts = {"AN", "CH", "DN", "DL", "JK", "LA", "LD", "PY"}
    assert len(set(state_dict.keys()).intersection(indian_states)) == 28
    assert len(set(state_dict.keys()).intersection(indian_uts)) == 8
