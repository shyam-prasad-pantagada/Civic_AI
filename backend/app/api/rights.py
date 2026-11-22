"""Civic_AI Local Laws and Citizen Rights Explainer API Router."""

from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.models.schemas import RightsRequest, RightsResponse
from app.services.rights_rag import rights_rag_service

router = APIRouter(tags=["rights"])


@router.post("/rights", response_model=RightsResponse)
async def explain_rights(
    payload: RightsRequest,
    lang: str = Query(default="en", description="Target language code"),
) -> RightsResponse:
    """Explain citizen rights and legal remedies with mandatory official citations.

    Every answer cites an official Act and Section, or returns no-source fallback.
    """
    effective_lang = payload.lang or lang or settings.DEFAULT_LANG
    if not settings.is_language_supported(effective_lang):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{effective_lang}' is not currently enabled in Civic_AI config.",
        )

    try:
        response = await rights_rag_service.query_rights(
            question=payload.question,
            state=payload.state,
            lang=effective_lang,
        )
        return response
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to query citizen rights: {e}")
