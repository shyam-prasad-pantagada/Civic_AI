"""Civic_AI Live Verification API Router."""

from fastapi import APIRouter, HTTPException, Query
from app.config import settings
from app.models.schemas import VerifyRequest, VerifyResponse
from app.services.verify import verification_service

router = APIRouter(tags=["verify"])


@router.post("/verify", response_model=VerifyResponse)
async def verify_circular(
    payload: VerifyRequest,
    lang: str = Query(default="en", description="Target language code"),
) -> VerifyResponse:
    """Verify latest status, circulars, and deadlines against live official government domains.

    Enforces domain allow-list restricted search and scraping.
    """
    effective_lang = payload.lang or lang or settings.DEFAULT_LANG
    if not settings.is_language_supported(effective_lang):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{effective_lang}' is not currently enabled in Civic_AI config.",
        )

    try:
        response = await verification_service.verify(
            claim_or_title=payload.claim_or_circular_title,
            source_url=payload.source_url,
            stated_deadline=payload.stated_deadline,
            state=payload.state,
            lang=effective_lang,
        )
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Verification failed: {e}")
