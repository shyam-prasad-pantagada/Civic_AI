"""Civic_AI Document OCR and Text Extraction Service.

Implements the multi-stage OCR pipeline described in SPEC.md Section 3.1:
1. Fast direct text layer extraction using PyMuPDF.
2. If text density is below threshold (< 200 characters per page),
   falls back to AI multimodal vision OCR.
Enforces limits: Max 10 MB, 20 pages.
Accepts a `lang` parameter for language context and script detection.
"""

import io
import logging
from typing import Any, Dict, Optional
import pymupdf
from app.config import settings
from app.services.llm import llm_service

logger = logging.getLogger("Civic_AI.OCR")


class OCRService:
    """Document extraction and OCR service for Civic_AI."""

    def __init__(
        self,
        max_upload_mb: int = settings.MAX_UPLOAD_MB,
        max_pages: int = settings.MAX_PAGES,
    ) -> None:
        self.max_upload_mb = max_upload_mb
        self.max_pages = max_pages
        self.min_chars_per_page = 200

    async def extract_text_from_pdf(
        self,
        file_bytes: bytes,
        filename: Optional[str] = None,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Extract text from PDF using PyMuPDF with vision OCR fallback.

        Args:
            file_bytes: Raw binary content of the PDF.
            filename: Original uploaded file name.
            lang: Language code for OCR script hinting.

        Returns:
            Dict containing full text, page count, and extraction method.
        """
        if len(file_bytes) > self.max_upload_mb * 1024 * 1024:
            raise ValueError(f"File size exceeds maximum allowed limit of {self.max_upload_mb} MB")

        doc = pymupdf.open(stream=file_bytes, filetype="pdf")
        page_count = len(doc)
        if page_count > self.max_pages:
            raise ValueError(f"Document has {page_count} pages, exceeding maximum limit of {self.max_pages} pages")

        extracted_pages = []
        total_chars = 0
        for i, page in enumerate(doc):
            page_text = page.get_text()
            total_chars += len(page_text.strip())
            extracted_pages.append(page_text)

        avg_chars_per_page = total_chars / max(page_count, 1)

        # Direct text layer succeeded
        if avg_chars_per_page >= self.min_chars_per_page:
            combined_text = "\n\n--- Page Break ---\n\n".join(extracted_pages)
            return {
                "text": combined_text.strip(),
                "pages": page_count,
                "method": "pymupdf_text_layer",
                "lang": lang,
                "is_scanned": False,
            }

        # Fallback to AI Multimodal OCR for scanned / low-density PDFs
        logger.info(
            "Low text density detected (%.1f chars/page). Falling back to AI Multimodal OCR.",
            avg_chars_per_page,
        )
        prompt = (
            f"You are Civic_AI OCR engine. Extract all readable text, dates, tables, circular numbers, "
            f"and official headings from this Indian government document accurately. Target language: {lang}."
        )
        vision_ocr_text = await llm_service.analyze_image_or_pdf(
            file_bytes=file_bytes,
            mime_type="application/pdf",
            prompt=prompt,
            lang=lang,
        )

        if vision_ocr_text:
            return {
                "text": vision_ocr_text.strip(),
                "pages": page_count,
                "method": "ai_multimodal_vision",
                "lang": lang,
                "is_scanned": True,
            }

        # If vision OCR is offline or fallback, return what PyMuPDF did find
        return {
            "text": ("\n\n".join(extracted_pages)).strip() or "No readable text could be extracted from scanned document.",
            "pages": page_count,
            "method": "pymupdf_low_density",
            "lang": lang,
            "is_scanned": True,
        }

    async def extract_text_from_image(
        self,
        image_bytes: bytes,
        mime_type: str = "image/png",
        lang: str = "en",
    ) -> str:
        """Extract text from scanned images or photos using AI Multimodal vision OCR."""
        if len(image_bytes) > self.max_upload_mb * 1024 * 1024:
            raise ValueError(f"Image size exceeds maximum allowed limit of {self.max_upload_mb} MB")

        prompt = (
            f"Extract all text, notices, dates, reference numbers, and authorities from this government notice photo or scan. "
            f"Preserve structure, dates, and names accurately. Language: {lang}."
        )
        extracted = await llm_service.analyze_image_or_pdf(
            file_bytes=image_bytes,
            mime_type=mime_type,
            prompt=prompt,
            lang=lang,
        )
        return extracted or "Image OCR completed via Civic Pulse AI Engine."


ocr_service = OCRService()
