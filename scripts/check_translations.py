#!/usr/bin/env python3
"""Civic_AI Translation Coverage & Quality Audit Script.

Audits pre-translated scheme data in `data/schemes.json` across all 12 official
Indian languages: en, hi, te, ta, kn, ml, mr, bn, gu, pa, or, ur.
Reports per-language and per-field coverage and fails (exit code 1) if any
record is missing a language or required translation.

Usage:
    python scripts/check_translations.py
"""

import json
import logging
from pathlib import Path
import sys
from typing import Any, Dict, List

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("Civic_AI.TranslationAudit")

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"

REQUIRED_REGIONAL_LANGS = [
    "hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa", "or", "ur"
]

LANGUAGE_NAMES = {
    "en": "English",
    "hi": "Hindi",
    "te": "Telugu",
    "ta": "Tamil",
    "kn": "Kannada",
    "ml": "Malayalam",
    "mr": "Marathi",
    "bn": "Bengali",
    "gu": "Gujarati",
    "pa": "Punjabi",
    "or": "Odia",
    "ur": "Urdu",
}


def audit_translations() -> int:
    """Run comprehensive translation coverage audit."""
    if not SCHEMES_FILE.exists():
        logger.error("❌ Schemes file not found at %s", SCHEMES_FILE)
        return 1

    with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
        schemes: List[Dict[str, Any]] = json.load(f)

    total_records = len(schemes)
    if total_records == 0:
        logger.error("❌ Schemes dataset is empty!")
        return 1

    logger.info("=" * 80)
    logger.info("🔍 Civic_AI Multilingual Translation Audit")
    logger.info("   Total Records: %d | Target Languages: 12 (en + 11 regional)", total_records)
    logger.info("=" * 80)

    # Metrics per language
    coverage: Dict[str, Dict[str, int]] = {
        lang: {
            "name": 0,
            "summary": 0,
            "ministry": 0,
            "benefits": 0,
            "eligibility": 0,
            "documents": 0,
            "total_present": 0,
        }
        for lang in REQUIRED_REGIONAL_LANGS
    }

    records_with_eligibility_en = 0
    records_with_benefits_en = 0
    records_with_documents_en = 0

    missing_lang_records: Dict[str, List[str]] = {lang: [] for lang in REQUIRED_REGIONAL_LANGS}
    missing_eligibility_records: Dict[str, List[str]] = {lang: [] for lang in REQUIRED_REGIONAL_LANGS}

    for s in schemes:
        sid = s.get("scheme_id", "UNKNOWN")
        en_has_eligibility = bool(s.get("eligibility_criteria"))
        en_has_benefits = bool(s.get("benefits"))
        en_has_docs = bool(s.get("documents_needed"))

        if en_has_eligibility:
            records_with_eligibility_en += 1
        if en_has_benefits:
            records_with_benefits_en += 1
        if en_has_docs:
            records_with_documents_en += 1

        translations = s.get("translations", {})
        if not isinstance(translations, dict):
            for lang in REQUIRED_REGIONAL_LANGS:
                missing_lang_records[lang].append(sid)
            continue

        for lang in REQUIRED_REGIONAL_LANGS:
            t = translations.get(lang)
            if not isinstance(t, dict):
                missing_lang_records[lang].append(sid)
                continue

            has_name = bool(t.get("scheme_name") and str(t.get("scheme_name")).strip())
            has_summary = bool(t.get("summary") and str(t.get("summary")).strip())
            has_ministry = bool(t.get("ministry") or t.get("nodal_authority"))

            if has_name:
                coverage[lang]["name"] += 1
            if has_summary:
                coverage[lang]["summary"] += 1
            if has_ministry:
                coverage[lang]["ministry"] += 1

            if has_name and has_summary:
                coverage[lang]["total_present"] += 1
            else:
                missing_lang_records[lang].append(sid)

            # Check detailed fields if English has them
            if t.get("benefits"):
                coverage[lang]["benefits"] += 1
            if t.get("eligibility_criteria"):
                coverage[lang]["eligibility"] += 1
            elif en_has_eligibility:
                missing_eligibility_records[lang].append(sid)

            if t.get("documents_required") or t.get("documents_needed"):
                coverage[lang]["documents"] += 1

    # Print Report Table
    logger.info(
        "\n%-6s %-12s %-12s %-12s %-12s %-12s %-12s %-10s",
        "Code", "Language", "Scheme Name", "Summary", "Ministry", "Benefits", "Eligibility", "Status"
    )
    logger.info("-" * 88)

    all_passed = True
    for lang in REQUIRED_REGIONAL_LANGS:
        c = coverage[lang]
        lang_name = LANGUAGE_NAMES.get(lang, lang)
        is_complete = (
            c["total_present"] == total_records
            and c["name"] == total_records
            and c["summary"] == total_records
            and c["ministry"] == total_records
            and (records_with_eligibility_en == 0 or c["eligibility"] >= records_with_eligibility_en)
        )
        status = "✅ PASS" if is_complete else "❌ FAIL"
        if not is_complete:
            all_passed = False

        logger.info(
            "%-6s %-12s %-12s %-12s %-12s %-12s %-12s %-10s",
            lang,
            lang_name,
            f"{c['name']}/{total_records}",
            f"{c['summary']}/{total_records}",
            f"{c['ministry']}/{total_records}",
            f"{c['benefits']}",
            f"{c['eligibility']}/{records_with_eligibility_en}",
            status,
        )

    logger.info("-" * 88)
    logger.info(
        "English baseline: %d records, %d with eligibility, %d with benefits, %d with documents.",
        total_records, records_with_eligibility_en, records_with_benefits_en, records_with_documents_en
    )

    if not all_passed:
        logger.error("\n❌ Translation Audit FAILED: Incomplete coverage detected.")
        for lang, missing in missing_lang_records.items():
            if missing:
                logger.error("  • Language '%s' (%s) missing %d schemes: %s",
                             lang, LANGUAGE_NAMES.get(lang), len(missing), missing[:5])
        for lang, missing in missing_eligibility_records.items():
            if missing:
                logger.error("  • Language '%s' missing eligibility for %d schemes: %s",
                             lang, len(missing), missing[:5])
        return 1

    logger.info("\n🎉 100%% Multilingual Translation Coverage Achieved across all %d schemes and 12 languages!", total_records)
    return 0


if __name__ == "__main__":
    sys.exit(audit_translations())
