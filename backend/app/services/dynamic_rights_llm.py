"""Dynamic LLM Fallback Service for Non-Statutory Citizen Rights & Policy Queries.

Invoked by RightsRAGService when a citizen's question does not match a direct
standalone Act in the static India Code RAG knowledgebase. Uses Gemini with
up-to-date Indian regulatory, institutional, and constitutional context, and
explicitly discloses that no standalone statutory Act file exists for the query.
"""

from datetime import datetime, timezone
import json
import logging
import os
import re
from typing import Optional

from google import genai
from google.genai import types

from app.config import settings
from app.models.schemas import RightsResponse

logger = logging.getLogger("Civic_AI.DynamicRightsLLM")


def _resolve_api_key() -> Optional[str]:
    """Resolve Gemini API key across common settings and environment variable names."""
    for candidate in (
        getattr(settings, "LLM_API_KEY", None),
        getattr(settings, "GEMINI_API_KEY", None),
        getattr(settings, "GOOGLE_API_KEY", None),
        os.getenv("LLM_API_KEY"),
        os.getenv("GEMINI_API_KEY"),
        os.getenv("GOOGLE_API_KEY"),
    ):
        if candidate and str(candidate).strip():
            return str(candidate).strip()
    return None


async def generate_dynamic_rights_guidance(
    question: str,
    state: Optional[str] = None,
    lang: str = "en",
) -> Optional[RightsResponse]:
    """Generate up-to-date non-statutory guidance via Gemini when RAG has no match."""
    api_key = _resolve_api_key()
    if not api_key:
        logger.warning(
            "No Gemini API key configured (checked LLM_API_KEY, GEMINI_API_KEY, GOOGLE_API_KEY); "
            "skipping dynamic rights LLM fallback."
        )
        return None

    current_date = datetime.now(timezone.utc).strftime("%B %d, %Y")
    jurisdiction = state if state else "Central Government (Nationwide)"

    prompt = f"""You are Civic_AI, an up-to-date Indian legal, regulatory, and citizen rights assistant (current date: {current_date}).

Citizen question: "{question}"
State / Jurisdiction context: {jurisdiction}
Target response language code: {lang}

Important context:
- This query did NOT match a direct standalone statutory Act in our India Code statutory RAG database.
- Provide accurate, practical, up-to-date guidance as of {current_date} covering applicable Indian institutional rules, government/regulatory guidelines (e.g., UGC, CBSE, state education departments, police/cyber rules, or local bylaws as relevant), and constitutional principles.
- Do NOT invent fake statutory Act filenames or fake section numbers.
- Write in clear, accessible Grade-6 language (in language '{lang}' if supported, otherwise English).

Return ONLY valid JSON with this exact structure:
{{
  "your_rights": [
    "Point 1 explaining the applicable institutional/regulatory rule or constitutional principle...",
    "Point 2...",
    "Point 3..."
  ],
  "what_you_can_do": [
    "Actionable step 1...",
    "Actionable step 2...",
    "Actionable step 3..."
  ],
  "where_to_complain_or_get_free_help": [
    "Relevant institutional/regulatory authority or official portal...",
    "National Legal Services Authority (NALSA) Toll-Free Legal Aid Helpline: 15100"
  ]
}}"""

    configured_model = (getattr(settings, "LLM_MODEL", None) or os.getenv("LLM_MODEL") or "").strip()
    candidate_models = []
    for m in (configured_model, "gemini-3.6-flash", "gemini-3.8-flash", "gemini-2.5-flash"):
        if m and m not in candidate_models:
            candidate_models.append(m)

    client = genai.Client(api_key=api_key)
    last_error = None

    for model_name in candidate_models:
        try:
            response = await client.aio.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    response_mime_type="application/json",
                ),
            )

            raw_text = (response.text or "").strip()
            raw_text = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw_text, flags=re.IGNORECASE).strip()
            data = json.loads(raw_text)

            rights_items = data.get("your_rights") or []
            if not rights_items:
                logger.warning("DynamicRightsLLM returned empty your_rights from model '%s'.", model_name)
                return None

            non_statutory_notice = (
                f"Not Directly Under Statutory Law (Dynamic AI Guidance • Updated {current_date}): "
                "No standalone statutory Act in the India Code repository directly governs this exact scenario; "
                "the points below reflect current Indian regulatory guidelines, institutional rules, and constitutional principles."
            )
            rights_items.insert(0, non_statutory_notice)

            return RightsResponse(
                question=question,
                your_rights=rights_items,
                what_you_can_do=data.get("what_you_can_do")
                or [
                    "Request a copy of the written institutional rule, circular, or policy governing the issue.",
                    "Consult your local District Legal Services Authority (DLSA) or NALSA (15100) for free legal advice.",
                ],
                where_to_complain_or_get_free_help=data.get("where_to_complain_or_get_free_help")
                or [
                    "Relevant Institutional Grievance Redressal Cell / Ombudsperson",
                    "National Legal Services Authority (NALSA) Toll-Free Legal Aid Helpline: 15100",
                ],
                citations=[],
                has_official_source=False,
                lang=lang,
            )
        except Exception as exc:
            last_error = exc
            logger.warning("DynamicRightsLLM attempt with model '%s' failed: %s", model_name, exc)
            continue

    logger.error("DynamicRightsLLM exhausted all models for query '%s': %s", question, last_error)
    return None
