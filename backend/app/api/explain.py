"""Civic_AI Notice and Document Explainer API Router."""

from datetime import datetime, timezone
import logging
from typing import Optional
from fastapi import APIRouter, File, Form, HTTPException, Query, UploadFile
from app.config import settings
from app.models.schemas import ExplainRequest, ExplainResponse
from app.services.explainer import explainer_service
from app.services.ocr import ocr_service

logger = logging.getLogger("Civic_AI.API.Explain")
router = APIRouter(tags=["explain"])


@router.post("/explain", response_model=ExplainResponse)
async def explain_notice(
    payload: ExplainRequest,
    lang: str = Query(default="en", description="Target language code"),
) -> ExplainResponse:
    """Explain a citizen notice, circular, or government PDF text in simple language.

    Accepts text or document URL and returns structured explanation.
    Ensures lang parameter is validated against supported languages.
    """
    effective_lang = payload.lang or lang or settings.DEFAULT_LANG
    if not settings.is_language_supported(effective_lang):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{effective_lang}' is not currently enabled in Civic_AI config.",
        )

    text_to_process = (payload.text or "").strip()
    if not text_to_process and not payload.document_url:
        raise HTTPException(
            status_code=400,
            detail="Either 'text' or 'document_url' must be provided.",
        )

    # If document_url is provided but no text, fetch or notify
    if not text_to_process and payload.document_url:
        text_to_process = f"Official Document URL: {payload.document_url}. Notice regarding government circular and citizen rights."

    try:
        result = await explainer_service.explain(
            document_text=text_to_process,
            document_url=payload.document_url,
            state=payload.state,
            lang=effective_lang,
        )
        return result
    except Exception as e:
        logger.error("Error explaining notice: %s", e)
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/explain/upload", response_model=ExplainResponse)
async def explain_uploaded_file(
    file: UploadFile = File(..., description="PDF, image, or document to explain"),
    state: Optional[str] = Form(default=None, description="State/UT code or Central"),
    lang: str = Form(default="en", description="Target language code"),
) -> ExplainResponse:
    """Upload a government notice file (PDF, PNG, JPG) to extract text and generate an explanation.

    Applies PyMuPDF text layer extraction with multimodal OCR fallback for scans.
    """
    effective_lang = lang or settings.DEFAULT_LANG
    if not settings.is_language_supported(effective_lang):
        raise HTTPException(
            status_code=400,
            detail=f"Language '{effective_lang}' is not currently enabled in Civic_AI config.",
        )

    file_bytes = await file.read()
    if not file_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    filename = file.filename or "uploaded_document"
    content_type = file.content_type or ""

    try:
        # Check if PDF
        if filename.lower().endswith(".pdf") or "pdf" in content_type:
            ocr_result = await ocr_service.extract_text_from_pdf(
                file_bytes=file_bytes,
                filename=filename,
                lang=effective_lang,
            )
            extracted_text = ocr_result["text"]
        elif any(ext in filename.lower() for ext in [".png", ".jpg", ".jpeg", ".webp"]) or "image" in content_type:
            mime = content_type if "image" in content_type else "image/png"
            extracted_text = await ocr_service.extract_text_from_image(
                image_bytes=file_bytes,
                mime_type=mime,
                lang=effective_lang,
            )
        else:
            # Fallback to text decoding
            try:
                extracted_text = file_bytes.decode("utf-8")
            except UnicodeDecodeError:
                extracted_text = file_bytes.decode("latin-1", errors="replace")

        result = await explainer_service.explain(
            document_text=extracted_text,
            document_url=f"Uploaded file: {filename}",
            state=state,
            lang=effective_lang,
        )
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error("Error processing uploaded document: %s", e)
        raise HTTPException(status_code=500, detail=f"Failed to process document: {e}")
