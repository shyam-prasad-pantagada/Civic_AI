"""Tests for Civic_AI Multilingual Scheme Directory & 12 Official Languages."""

from fastapi.testclient import TestClient


def test_languages_endpoint_returns_12_enabled_languages(client: TestClient):
    """Verify that all 12 official languages are enabled with proper native names."""
    response = client.get("/api/languages")
    assert response.status_code == 200
    data = response.json()
    assert "languages" in data
    langs = data["languages"]

    # Verify all 12 mandatory official languages are present and enabled
    mandatory_codes = ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa", "or", "ur"]
    for code in mandatory_codes:
        assert code in langs, f"Language {code} missing from config"
        assert langs[code]["enabled"] is True, f"Language {code} must be enabled"


def test_schemes_directory_with_language_parameter(client: TestClient):
    """Verify /api/schemes?lang=hi returns localized scheme names and summaries."""
    response = client.get("/api/schemes?lang=hi")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) > 0

    # Find at least one scheme with localized Hindi translation
    hindi_schemes = [s for s in schemes if s.get("original_scheme_name")]
    assert len(hindi_schemes) > 0
    sample = hindi_schemes[0]
    assert sample["scheme_name"] != sample["original_scheme_name"]


def test_scheme_detail_with_regional_language(client: TestClient):
    """Verify /api/schemes/{scheme_id}?lang=te returns localized Telugu details."""
    response = client.get("/api/schemes")
    schemes = response.json()
    # Find a scheme with translations
    translated_schemes = [s for s in schemes if s.get("translations")]
    assert len(translated_schemes) > 0
    scheme_id = translated_schemes[0]["scheme_id"]

    res_te = client.get(f"/api/schemes/{scheme_id}?lang=te")
    assert res_te.status_code == 200
    detail = res_te.json()
    assert detail["scheme_id"] == scheme_id
    assert "translations" in detail


def test_search_schemes_with_regional_script(client: TestClient):
    """Verify searching with Hindi Devanagari script returns matching schemes."""
    response = client.get("/api/schemes?search=किसान")
    assert response.status_code == 200
    schemes = response.json()
    assert len(schemes) > 0


def test_batch_translate_schemes(client: TestClient):
    """Verify /api/schemes/batch-translate returns translated schemes with lexicon/caching."""
    payload = {"scheme_ids": ["PM-KISAN"], "lang": "hi"}
    response = client.post("/api/schemes/batch-translate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "translations" in data
    assert "PM-KISAN" in data["translations"]
    trans = data["translations"]["PM-KISAN"]
    assert trans["scheme_id"] == "PM-KISAN"
    assert "scheme_name" in trans


def test_all_i18n_keys_present_in_all_languages():
    """Verify every UI translation key exists across all 12 supported languages."""
    import re
    from pathlib import Path

    js_file = Path(__file__).resolve().parents[2] / "frontend" / "src" / "i18n" / "translations.js"
    assert js_file.exists(), f"translations.js not found at {js_file}"

    # Read JS file and extract language dictionaries
    with open(js_file, "r", encoding="utf-8") as f:
        content = f.read()

    # Match each language block: "en": { ... }
    supported = ["en", "hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa", "or", "ur"]
    key_pattern = re.compile(r'"([a-zA-Z0-9_-]+)":\s*(?:"|\'|`|\[|true|false|\{)')

    lang_keys = {}
    for code in supported:
        match = re.search(rf'"{code}":\s*\{{([^}}]+(?:\{{[^}}]*\}}[^}}]*)*)\}}', content)
        if match:
            block = match.group(1)
            keys = set(key_pattern.findall(block))
            lang_keys[code] = keys

    assert "en" in lang_keys, "English dictionary missing"
    en_keys = lang_keys["en"]
    assert len(en_keys) > 100, f"Expected > 100 English keys, found {len(en_keys)}"

    for code in supported:
        assert code in lang_keys, f"Language {code} missing from translations.js"
        missing = en_keys - lang_keys[code]
        assert len(missing) == 0, f"Language {code} missing keys: {missing}"


