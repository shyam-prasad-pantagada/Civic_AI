"""Tests for Civic_AI Public Schemes Directory and Search API."""

import pytest
from fastapi.testclient import TestClient


def test_list_schemes_all(client: TestClient):
    """Test retrieving all schemes from public directory."""
    response = client.get("/api/schemes")
    assert response.status_code == 200
    schemes = response.json()
    assert isinstance(schemes, list)
    assert len(schemes) >= 15
    for s in schemes:
        assert "scheme_id" in s
        assert "scheme_name" in s
        assert "official_link" in s
        assert "benefits" in s


def test_filter_schemes_central(client: TestClient):
    """Test filtering by central jurisdiction."""
    response = client.get("/api/schemes?jurisdiction=central")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) > 0
    for s in schemes:
        assert s["state"] == "Central"


def test_filter_schemes_by_state(client: TestClient):
    """Test filtering by specific state (Maharashtra)."""
    response = client.get("/api/schemes?jurisdiction=state&state=MH")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 2
    for s in schemes:
        assert s["state"] == "MH"


def test_search_schemes_by_keyword(client: TestClient):
    """Test instant keyword search for 'kisan'."""
    response = client.get("/api/schemes?search=kisan")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) >= 1
    ids = [s["scheme_id"] for s in schemes]
    assert "PM-KISAN" in ids


def test_get_scheme_by_id_success(client: TestClient):
    """Test retrieving full 8-point policy breakdown by ID."""
    response = client.get("/api/schemes/PM-JAY")
    assert response.status_code == 200
    scheme = response.json()
    assert scheme["scheme_id"] == "PM-JAY"
    assert "Ayushman Bharat" in scheme["scheme_name"]
    assert "ministry" in scheme
    assert "summary" in scheme
    assert len(scheme["benefits"]) > 0
    assert len(scheme["eligibility_criteria"]) > 0
    assert len(scheme["documents_needed"]) > 0
    assert scheme["official_link"].startswith("https://")


def test_get_scheme_by_id_not_found(client: TestClient):
    """Test non-existent scheme returns 404."""
    response = client.get("/api/schemes/NONEXISTENT_XYZ")
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


def test_schemes_server_side_pagination(client: TestClient):
    """Verify server-side pagination with page and page_size query parameters."""
    response = client.get("/api/schemes?page=1&page_size=24")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert "items" in data
    assert "total" in data
    assert "page" in data
    assert "page_size" in data
    assert "total_pages" in data
    assert data["page"] == 1
    assert data["page_size"] == 24
    assert len(data["items"]) == 24
    assert data["total"] > 1000
    assert data["total_pages"] == (data["total"] + 23) // 24


def test_schemes_filter_by_governance_type(client: TestClient):
    """Verify filtering schemes by governance classification."""
    for stype in ["central", "state", "integrated", "multi_state"]:
        res = client.get(f"/api/schemes?scheme_type={stype}")
        assert res.status_code == 200
        schemes = res.json()
        assert len(schemes) > 0
        for s in schemes:
            assert s.get("scheme_type") == stype or (stype == "state" and s.get("scheme_type") in ("state", "local"))


def test_fast_sqlite_fts5_search(client: TestClient):
    """Verify sub-second SQLite FTS5 search across schemes."""
    import time
    t0 = time.perf_counter()
    res = client.get("/api/schemes?search=farmer")
    elapsed = time.perf_counter() - t0
    assert res.status_code == 200
    schemes = res.json()
    assert len(schemes) > 0
    assert elapsed < 1.0, f"Search took too long: {elapsed:.2f}s"

