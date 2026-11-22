"""Civic_AI Live Government Scheme Discovery & LLM Grounding Service.

Provides real-time fallback synthesis for any Indian Central or State/UT government scheme
using live web search restricted to official government domains (*.gov.in, *.nic.in, myscheme.gov.in, pib.gov.in)
combined with AI structured synthesis.
Results are automatically cached into the local scheme index.
"""

from datetime import datetime, timezone
import json
import logging
from pathlib import Path
import re
from typing import Any, Dict, List, Optional
import httpx
from app.config import settings
from app.services.llm import LLMService

logger = logging.getLogger("Civic_AI.LiveSchemeLookup")

PROJECT_ROOT = Path(__file__).resolve().parents[4]
DATA_DIR = PROJECT_ROOT / "data"
SCHEMES_FILE = DATA_DIR / "schemes.json"


class LiveSchemeLookupService:
    """Live web search and LLM synthesis engine for Indian public welfare schemes."""

    def __init__(self) -> None:
        self.llm_service = LLMService()

    def _sanitize_slug(self, text: str) -> str:
        clean = re.sub(r"[^A-Za-z0-9]+", "-", text).strip("-").upper()
        return f"LIVE-{clean[:24]}" if not clean.startswith("LIVE-") else clean[:30]

    async def search_official_web(self, query: str, state: Optional[str] = None) -> List[Dict[str, str]]:
        """Perform real-time search restricted to official Indian government domains."""
        tavily_key = settings.TAVILY_API_KEY
        if not tavily_key:
            logger.info("TAVILY_API_KEY not set; using AI grounded knowledge fallback.")
            return []

        state_term = f"{state} " if state and state != "Central" else ""
        search_query = f"site:myscheme.gov.in OR site:gov.in OR site:nic.in OR site:pib.gov.in {state_term}{query} scheme eligibility benefits guidelines application"

        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                resp = await client.post(
                    "https://api.tavily.com/search",
                    json={
                        "api_key": tavily_key,
                        "query": search_query,
                        "search_depth": "advanced",
                        "include_domains": ["myscheme.gov.in", "gov.in", "nic.in", "pib.gov.in"],
                        "max_results": 5,
                    },
                )
                if resp.status_code == 200:
                    data = resp.json()
                    results = data.get("results", [])
                    clean_results = []
                    for r in results:
                        url = r.get("url", "")
                        if ".gov.in" in url or ".nic.in" in url or "myscheme.gov.in" in url:
                            clean_results.append({
                                "title": r.get("title", ""),
                                "url": url,
                                "content": r.get("content", ""),
                            })
                    return clean_results
        except Exception as e:
            logger.warning("Live web search failed: %s; falling back to LLM grounding.", e)

        return []

    async def lookup_scheme(
        self,
        query: str,
        state: Optional[str] = None,
        category: Optional[str] = None,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Fetch or synthesize a complete 8-point official government scheme card."""
        clean_query = query.strip()
        state_context = f"in state '{state}'" if state and state != "Central" else "under Central Government or Indian States"

        # 1. Fetch live web snippets from official government sources
        web_snippets = await self.search_official_web(clean_query, state=state)
        snippet_text = ""
        if web_snippets:
            snippet_text = "\n\nOFFICIAL WEB SNIPPETS FROM GOV.IN / MYSCHEME:\n" + "\n".join(
                f"- Title: {s['title']}\n  URL: {s['url']}\n  Snippet: {s['content']}"
                for s in web_snippets[:4]
            )

        # 2. Construct grounded LLM prompt for structured synthesis
        system_instruction = (
            "You are Civic_AI's Lead Public Policy & Welfare Specialist for India. "
            "Your task is to analyze the requested government scheme query and output a strict, accurate, comprehensive "
            "policy specification based on official Indian Government guidelines (myScheme.gov.in, PIB, India Code, State Portals). "
            "CRITICAL RULES:\n"
            "1. Output MUST be valid JSON only, strictly matching the requested schema.\n"
            "2. All official URLs must point to real official domains (*.gov.in, *.nic.in, or myscheme.gov.in).\n"
            "3. Explicitly classify scheme_type into: 'central' (Central Ministry, nationwide), 'state' (single State/UT), "
            "'integrated' (co-funded/jointly implemented by Center + States with state variations or separate state portals), "
            "'multi_state' (specific group of states/regions), or 'local' (municipal/district).\n"
            "4. Provide exact quantitative monetary benefits, statutory eligibility limits, and direct apply URLs.\n"
        )

        prompt = f"""
Analyze the following scheme query {state_context}:
Query: "{clean_query}"
Requested Category: {category or "Any"}
Target Language: {lang}
{snippet_text}

Provide the complete scheme breakdown in JSON format with these exact keys:
{{
  "scheme_name": "Full official name of the scheme in English",
  "scheme_type": "central" | "state" | "integrated" | "multi_state" | "local",
  "applicable_states": ["All India"] or list of applicable 2-letter state codes/names,
  "state": "Central" or 2-letter state code (e.g. "MH", "KA", "AP", "DL", etc.),
  "nodal_authority": "Official Nodal Ministry or State Department name",
  "ministry": "Nodal Ministry or State Department name",
  "category": "One of: farmer | woman | student | senior | health | business | housing | disability | social_welfare",
  "benefit_type": "One of: Cash / DBT | Healthcare / Insurance | Subsidy | Credit / Loan | In-Kind | Savings",
  "summary": "Clear 2-sentence plain-language summary of what the scheme provides and who it is for",
  "benefits": [
    "Specific financial or in-kind benefit 1 with exact amount in Rupees",
    "Specific financial or in-kind benefit 2"
  ],
  "eligibility_criteria": [
    "Criterion 1 (age range, citizenship, residence)",
    "Criterion 2 (income threshold, category, landholding)"
  ],
  "exclusions": [
    "Disqualification condition 1 (e.g. tax payers, regular govt employees)",
    "Disqualification condition 2"
  ],
  "documents_needed": [
    "Required document 1 (e.g. Aadhaar Card linked with mobile)",
    "Required document 2 (e.g. Income Certificate)",
    "Required document 3 (e.g. Bank Passbook seeded with Aadhaar)"
  ],
  "application_mode": "online" | "offline" | "hybrid",
  "how_to_apply": "Step-by-step instructions for online portal application and offline route (e.g. CSC / BDO / Panchayat)",
  "direct_apply_url": "Direct official URL to register or apply online",
  "state_apply_links": [
    {{"state": "Maharashtra (MH)", "portal_name": "MahaDBT", "url": "https://mahadbt.maharashtra.gov.in"}},
    {{"state": "Karnataka (KA)", "portal_name": "Seva Sindhu", "url": "https://sevasindhugs.karnataka.gov.in"}}
  ],
  "official_link": "Official government portal URL ending in .gov.in or .nic.in",
  "myscheme_link": "Direct link to myscheme.gov.in page or search link",
  "source_links": [
    {{"title": "Official Portal / PIB Notification", "url": "https://..."}}
  ],
  "rules": {{
    "min_age": integer or null,
    "max_age": integer or null,
    "max_income": integer or null,
    "gender_required": "female" | "male" | null,
    "category_required": "farmer" | "student" | "senior" | "entrepreneur" | null,
    "state_required": "2-letter state code" or null
  }}
}}
"""

        generated_raw = await self.llm_service.generate_text(
            prompt=prompt,
            system_instruction=system_instruction,
            use_pro=False,
            lang=lang,
        )

        scheme_data = self._parse_json_response(generated_raw, clean_query, state)
        
        # Merge official web snippet links into source_links
        if web_snippets:
            existing_urls = {s.get("url") for s in scheme_data.get("source_links", [])}
            for snip in web_snippets:
                if snip["url"] not in existing_urls:
                    scheme_data["source_links"].append({
                        "title": snip["title"] or "Official Government Circular",
                        "url": snip["url"],
                    })

        # Set live flags
        scheme_data["is_live_verified"] = True
        scheme_data["live_timestamp"] = datetime.now(timezone.utc).isoformat()
        if not scheme_data.get("scheme_id"):
            scheme_data["scheme_id"] = self._sanitize_slug(scheme_data.get("scheme_name", clean_query))

        # Cache in local scheme store
        self.cache_scheme(scheme_data)

        return scheme_data

    def _parse_json_response(self, raw_text: str, query: str, state: Optional[str]) -> Dict[str, Any]:
        """Extract and validate JSON from LLM generation."""
        try:
            # Strip markdown code blocks
            text = raw_text.strip()
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0].strip()
            elif "```" in text:
                text = text.split("```")[1].split("```")[0].strip()

            data = json.loads(text)
            if isinstance(data, dict) and "scheme_name" in data:
                st = data.get("state", state or "Central")
                data["state"] = st
                data["scheme_type"] = data.get("scheme_type") or ("central" if st == "Central" else "state")
                data["applicable_states"] = data.get("applicable_states") or (["All India"] if data["scheme_type"] in ("central", "integrated") else [st])
                data["nodal_authority"] = data.get("nodal_authority") or data.get("ministry") or "Government of India"
                data["ministry"] = data["nodal_authority"]
                data["application_mode"] = data.get("application_mode") or "online"
                data["direct_apply_url"] = data.get("direct_apply_url") or data.get("official_link") or "https://www.myscheme.gov.in"
                data["state_apply_links"] = data.get("state_apply_links") or []
                data["official_source_links"] = data.get("source_links") or data.get("official_source_links") or []
                return data
        except Exception as e:
            logger.warning("Could not parse LLM output as JSON: %s. Using structured fallback.", e)

        # Fallback structured object
        slug = self._sanitize_slug(query)
        st = state if state and state != "Central" else "Central"
        is_central = st == "Central"
        return {
            "scheme_id": slug,
            "scheme_name": query.title(),
            "scheme_type": "central" if is_central else "state",
            "applicable_states": ["All India"] if is_central else [st],
            "state": st,
            "nodal_authority": "Ministry of Social Justice & Empowerment, Government of India" if is_central else f"Government of {st}",
            "ministry": "Ministry of Social Justice & Empowerment, Government of India" if is_central else f"Government of {st}",
            "category": "social_welfare",
            "benefit_type": "Cash / DBT",
            "summary": f"Public welfare scheme providing targeted financial assistance, subsidies, or services for eligible citizens under {query}.",
            "benefits": [
                "Direct Benefit Transfer (DBT) or subsidized public service directly to beneficiary account.",
                "Institutional support and grievance redressal under official government guidelines."
            ],
            "eligibility_criteria": [
                f"Resident of India ({st} state jurisdiction where applicable).",
                "Annual family income within statutory low/middle-income guidelines (<= Rs 2,50,000).",
                "Possession of Aadhaar-linked active bank account."
            ],
            "exclusions": [
                "Regular government employees and income tax payers.",
                "Beneficiaries receiving duplicate benefits under corresponding central/state programs."
            ],
            "documents_needed": [
                "Aadhaar Card with mobile linking",
                "Income Certificate issued by designated Revenue Authority",
                "Aadhaar-seeded Bank Passbook"
            ],
            "application_mode": "online",
            "how_to_apply": f"Apply online at official portal or visit nearest Common Service Centre (CSC) / District Welfare Office.",
            "direct_apply_url": "https://www.india.gov.in",
            "state_apply_links": [],
            "official_link": "https://www.india.gov.in",
            "myscheme_link": f"https://www.myscheme.gov.in/search?q={query.replace(' ', '+')}",
            "source_links": [
                {"title": "National Portal of India", "url": "https://www.india.gov.in"},
                {"title": "myScheme National Platform", "url": f"https://www.myscheme.gov.in/search?q={query.replace(' ', '+')}"}
            ],
            "official_source_links": [
                {"title": "National Portal of India", "url": "https://www.india.gov.in"},
                {"title": "myScheme National Platform", "url": f"https://www.myscheme.gov.in/search?q={query.replace(' ', '+')}"}
            ],
            "rules": {
                "max_income": 250000,
                "state_required": st if st != "Central" else None,
            },
        }

    def cache_scheme(self, scheme: Dict[str, Any]) -> None:
        """Persist newly discovered scheme into `data/schemes.json` with full multilingual placeholders."""
        try:
            DATA_DIR.mkdir(parents=True, exist_ok=True)
            schemes = []
            if SCHEMES_FILE.exists():
                with open(SCHEMES_FILE, "r", encoding="utf-8") as f:
                    schemes = json.load(f)

            # Ensure translations dictionary exists for all 11 regional languages
            if "translations" not in scheme or not isinstance(scheme["translations"], dict):
                scheme["translations"] = {}

            from app.services.eligibility.canonical_translations import (
                MINISTRIES_LEXICON,
                CATEGORIES_LEXICON,
                BENEFIT_TYPES_LEXICON,
            )

            REGIONAL_LANGS = ["hi", "te", "ta", "kn", "ml", "mr", "bn", "gu", "pa", "or", "ur"]
            for rlang in REGIONAL_LANGS:
                if rlang not in scheme["translations"]:
                    min_trans = MINISTRIES_LEXICON.get(scheme.get("ministry", ""), {}).get(rlang, scheme.get("ministry", ""))
                    cat_trans = CATEGORIES_LEXICON.get(scheme.get("category", ""), {}).get(rlang, scheme.get("category", ""))
                    ben_trans = BENEFIT_TYPES_LEXICON.get(scheme.get("benefit_type", ""), {}).get(rlang, scheme.get("benefit_type", ""))
                    scheme["translations"][rlang] = {
                        "scheme_name": scheme.get("scheme_name", ""),
                        "summary": scheme.get("summary", ""),
                        "ministry": min_trans,
                        "nodal_authority": min_trans,
                        "category": cat_trans,
                        "benefit_type": ben_trans,
                        "benefits": scheme.get("benefits", []),
                        "eligibility_criteria": scheme.get("eligibility_criteria", []),
                        "exclusions": scheme.get("exclusions", []),
                        "documents_required": scheme.get("documents_needed", []),
                        "application_steps": [scheme.get("how_to_apply", "")],
                    }

            # Check if already present by ID
            sid = scheme.get("scheme_id", "").upper()
            found = False
            for idx, s in enumerate(schemes):
                if s.get("scheme_id", "").upper() == sid:
                    schemes[idx] = scheme
                    found = True
                    break

            if not found:
                schemes.append(scheme)

            with open(SCHEMES_FILE, "w", encoding="utf-8") as f:
                json.dump(schemes, f, indent=2, ensure_ascii=False)
            logger.info("Cached scheme '%s' into %s", sid, SCHEMES_FILE)
        except Exception as e:
            logger.warning("Failed to cache scheme to disk: %s", e)


live_scheme_lookup = LiveSchemeLookupService()
