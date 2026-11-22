"""Civic_AI Scheme Eligibility Checker, All-India Directory & Live LLM Lookup Router."""

from typing import Any, Dict, List, Optional, Union
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel, Field
from app.config import settings
from app.models.schemas import (
    EligibilityRequest,
    EligibilityResponse,
)
from app.services.eligibility.engine import eligibility_engine
from app.services.eligibility.live_lookup import live_scheme_lookup
from app.services.eligibility.translator import scheme_translator

router = APIRouter(tags=["eligibility"])


class BatchTranslateRequest(BaseModel):
    scheme_ids: List[str] = Field(..., description="List of scheme IDs to translate")
    lang: str = Field(..., description="Target language code")


class SchemeLiveLookupRequest(BaseModel):
    query: str = Field(..., description="Scheme name, acronym, or citizen benefit requirement")
    state: Optional[str] = Field(default=None, description="Target state/UT code or 'Central'")
    category: Optional[str] = Field(default=None, description="Target citizen category")
    force_live: bool = Field(default=False, description="Bypass local cache and force live web search")
    lang: str = Field(default="en", description="Target language code")


@router.get("/schemes", response_model=Union[Dict[str, Any], List[Dict[str, Any]]])
async def list_schemes(
    search: Optional[str] = Query(default=None, description="Keyword search across scheme title, ministry, summary"),
    jurisdiction: Optional[str] = Query(default="all", description="'all' | 'central' | 'state'"),
    scheme_type: Optional[str] = Query(default=None, description="'central' | 'state' | 'integrated' | 'multi_state'"),
    level: Optional[str] = Query(default=None, description="'Central' | 'State'"),
    state: Optional[str] = Query(default=None, description="State/UT code (e.g. MH, KA, DL, UP)"),
    category: Optional[str] = Query(default=None, description="Scheme category (farmer, woman, health, student, etc.)"),
    benefit_type: Optional[str] = Query(default=None, description="Filter by benefit type (cash, in-kind, loan, etc.)"),
    live_fallback: bool = Query(default=False, description="Automatically trigger Live Web + LLM fallback if zero matches"),
    lang: str = Query(default="en", description="Target language code"),
    page: Optional[int] = Query(default=None, description="1-based page number for server-side pagination"),
    page_size: int = Query(default=24, description="Page size for server-side pagination"),
) -> Union[Dict[str, Any], List[Dict[str, Any]]]:
    """Browse and filter the public welfare scheme directory with cascading parameters."""
    results = eligibility_engine.get_schemes_directory(
        search=search,
        jurisdiction=jurisdiction,
        scheme_type=scheme_type,
        level=level,
        state=state,
        category=category,
        benefit_type=benefit_type,
        lang=lang,
        page=page,
        page_size=page_size,
    )

    # If requested and 0 results found, trigger live fallback
    is_paginated = isinstance(results, dict)
    items_count = len(results["items"]) if is_paginated else len(results)

    if items_count == 0 and search and live_fallback:
        try:
            live_scheme = await live_scheme_lookup.lookup_scheme(
                query=search,
                state=state,
                category=category,
                lang=lang,
            )
            if live_scheme:
                if is_paginated:
                    results["items"].append(live_scheme)
                    results["total"] += 1
                else:
                    results.append(live_scheme)
        except Exception:
            pass

    return results


@router.post("/schemes/live-lookup", response_model=Dict[str, Any])
async def live_scheme_lookup_endpoint(payload: SchemeLiveLookupRequest) -> Dict[str, Any]:
    """Live web search + LLM fallback for newly announced or unindexed government schemes."""
    clean_query = payload.query.strip()
    if not clean_query:
        raise HTTPException(status_code=400, detail="Search query cannot be empty.")

    # If force_live is not requested, check exact scheme ID or name in local index
    if not payload.force_live:
        for s in eligibility_engine.get_all_schemes():
            if (
                s.get("scheme_id", "").upper() == clean_query.upper()
                or s.get("scheme_name", "").lower() == clean_query.lower()
            ):
                res = s.copy()
                return res

    # Synthesize via Live Web Search (*.gov.in / myscheme.gov.in) + AI model
    result = await live_scheme_lookup.lookup_scheme(
        query=clean_query,
        state=payload.state,
        category=payload.category,
        lang=payload.lang,
    )
    return result


@router.post("/schemes/batch-translate", response_model=Dict[str, Any])
async def batch_translate_schemes(payload: BatchTranslateRequest) -> Dict[str, Any]:
    """Translate multiple schemes for visible cards or list views."""
    lang = payload.lang
    if not lang or lang == "en":
        return {"translations": {}}

    translations = {}
    for sid in payload.scheme_ids:
        scheme = eligibility_engine.get_scheme_by_id(sid, lang="en")
        if scheme:
            trans = await scheme_translator.translate_scheme(scheme, lang)
            translations[sid.upper()] = trans
    return {"translations": translations}


@router.get("/schemes/{scheme_id}", response_model=Dict[str, Any])
async def get_scheme_details(
    scheme_id: str,
    lang: str = Query(default="en", description="Target language code"),
) -> Dict[str, Any]:
    """Retrieve complete policy details, eligibility criteria, and application procedure for a scheme."""
    scheme = eligibility_engine.get_scheme_by_id(scheme_id, lang="en")
    if not scheme:
        raise HTTPException(
            status_code=404,
            detail=f"Scheme with ID '{scheme_id}' was not found in the public registry.",
        )
    if lang and lang != "en":
        scheme = await scheme_translator.translate_scheme(scheme, lang)
    return scheme


@router.post("/eligibility", response_model=EligibilityResponse)
async def check_eligibility(
    payload: EligibilityRequest,
    lang: str = Query(default="en", description="Target language code"),
) -> EligibilityResponse:
    """Evaluate citizen eligibility for central and state schemes using deterministic rules.

    Pure deterministic engine without LLM decisions; LLM handles explanation only.
    """
    effective_lang = payload.lang or lang or settings.DEFAULT_LANG
    if not settings.is_language_supported(effective_lang):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{effective_lang}' is not currently enabled in Civic_AI config.",
        )

    results, follow_ups = eligibility_engine.evaluate_all(
        profile=payload.profile,
        state_filter=payload.state or payload.profile.state,
        category_filter=payload.scheme_category or payload.profile.category,
        lang=effective_lang,
    )

    return EligibilityResponse(
        results=results,
        follow_up_questions=follow_ups,
        lang=effective_lang,
    )
