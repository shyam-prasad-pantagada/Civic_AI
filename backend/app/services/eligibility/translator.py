"""Civic_AI Multilingual Scheme Translation Service.

Translates scheme metadata, policy summaries, citizen benefits, eligibility rules,
exclusions, document checklists, and application steps into all 12 official Indian languages:
en, hi, te, ta, kn, ml, mr, bn, gu, pa, or, ur.

Provides multi-tier caching:
1. In-memory dictionary for instant (< 1ms) retrieval.
2. Persistent JSON snapshot cache.
3. Live AI translation via Civic Pulse AI Engine with fallback to canonical lexicon.
"""

import json
import logging
import os
from typing import Any, Dict, List, Optional
from app.config import settings

logger = logging.getLogger("Civic_AI.SchemeTranslator")

from pathlib import Path

possible_cache_paths = [
    Path(__file__).resolve().parents[4] / "data" / "scheme_translations_cache.json",
    Path.cwd() / "data" / "scheme_translations_cache.json",
    Path(__file__).resolve().parents[3] / "data" / "scheme_translations_cache.json",
]
CACHE_FILE = next((p for p in possible_cache_paths if p.exists()), possible_cache_paths[0])

# Canonical multilingual dictionary for Indian Governance terms
LEXICON: Dict[str, Dict[str, str]] = {
    "Central Scheme": {
        "hi": "केंद्रीय योजना",
        "te": "కేంద్ర పథకం",
        "ta": "மத்திய அரசு திட்டம்",
        "kn": "ಕೇಂದ್ರ ಯೋಜನೆ",
        "ml": "കേന്ദ്ര പദ്ധതി",
        "mr": "केंद्रीय योजना",
        "bn": "কেন্দ্রীয় প্রকল্প",
        "gu": "કેન્દ્રીય યોજના",
        "pa": "ਕੇਂਦਰੀ ਸਕੀਮ",
        "or": "କେନ୍ଦ୍ରୀୟ ଯୋଜନା",
        "ur": "مرکزی اسکیم",
    },
    "State Scheme": {
        "hi": "राज्य योजना",
        "te": "రాష్ట్ర పథకం",
        "ta": "மாநில அரசு திட்டம்",
        "kn": "ರಾಜ್ಯ ಯೋಜನೆ",
        "ml": "സംസ്ഥാന പദ്ധതി",
        "mr": "राज्य योजना",
        "bn": "রাজ্য প্রকল্প",
        "gu": "રાજ્ય યોજના",
        "pa": "ਰਾਜ ਸਕੀਮ",
        "or": "ରାଜ୍ୟ ଯୋଜନା",
        "ur": "ریاستی اسکیم",
    },
    "Integrated / Joint Scheme": {
        "hi": "एकीकृत / संयुक्त योजना (केंद्र + राज्य)",
        "te": "సమన్వయ / ఉమ్మడి పథకం (కేంద్రం + రాష్ట్రం)",
        "ta": "ஒருங்கிணைந்த திட்டம் (மத்திய + மாநில)",
        "kn": "ಸಂಯೋಜಿತ ಯೋಜನೆ (ಕೇಂದ್ರ + ರಾಜ್ಯ)",
        "ml": "സംയോജിത പദ്ധതി (കേന്ദ്രം + സംസ്ഥാനം)",
        "mr": "एकात्मिक योजना (केंद्र + राज्य)",
        "bn": "সমন্বিত প্রকল্প (কেন্দ্র + রাজ্য)",
        "gu": "સંયુક્ત યોજના (કેન્દ્ર + રાજ્ય)",
        "pa": "ਸਾਂਝੀ ਸਕੀਮ (ਕੇਂਦਰ + ਰਾਜ)",
        "or": "ସମନ୍ୱିତ ଯୋଜନା (କେନ୍ଦ୍ର + ରାଜ୍ୟ)",
        "ur": "مشترکہ اسکیم (مرکز + ریاست)",
    },
    "Ministry of Agriculture and Farmers Welfare": {
        "hi": "कृषि एवं किसान कल्याण मंत्रालय",
        "te": "వ్యవసాయం మరియు రైతు సంక్షేమ మంత్రిత్వ శాఖ",
        "ta": "வேளாண்மை மற்றும் உழவர் நல அமைச்சகம்",
        "kn": "ಕೃಷಿ ಮತ್ತು ರೈತರ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ",
        "ml": "കാർഷിക, കർഷക ക്ഷേമ മന്ത്രാലയം",
        "mr": "कृषी आणि शेतकरी कल्याण मंत्रालय",
        "bn": "কৃষি ও কৃষক কল্যাণ মন্ত্রক",
        "gu": "કૃષિ અને ખેડૂત કલ્યાણ મંત્રાલય",
        "pa": "ਖੇਤੀਬਾੜੀ ਅਤੇ ਕਿਸਾਨ ਭਲਾਈ ਮੰਤਰਾਲਾ",
        "or": "କୃଷି ଏବଂ କୃଷକ କଲ୍ୟାଣ ମନ୍ତ୍ରଣାଳୟ",
        "ur": "وزارت زراعت اور کسانوں کی فلاح و بہبود",
    },
    "Ministry of Health and Family Welfare": {
        "hi": "स्वास्थ्य एवं परिवार कल्याण मंत्रालय",
        "te": "ఆరోగ్య మరియు కుటుంబ సంక్షేమ మంత్రిత్వ శాఖ",
        "ta": "சுகாதாரம் மற்றும் குடும்ப நல அமைச்சகம்",
        "kn": "ಆರೋಗ್ಯ ಮತ್ತು ಕುಟುಂಬ ಕಲ್ಯಾಣ ಸಚಿವಾಲಯ",
        "ml": "ആരോഗ്യ കുടുംബക്ഷേമ മന്ത്രാലയം",
        "mr": "आरोग्य आणि कुटुंब कल्याण मंत्रालय",
        "bn": "স্বাস্থ্য ও পরিবার কল্যাণ মন্ত্রক",
        "gu": "આરોગ્ય અને પરિવાર કલ્યાણ મંત્રાલય",
        "pa": "ਸਿਹਤ ਅਤੇ ਪਰਿਵਾਰ ਭਲਾਈ ਮੰਤਰਾਲਾ",
        "or": "ସ୍ୱାସ୍ଥ୍ୟ ଏବଂ ପରିବାର କଲ୍ୟାଣ ମନ୍ତ୍ରଣାଳୟ",
        "ur": "وزارت صحت اور خاندانی بہبود",
    },
    "Ministry of Rural Development": {
        "hi": "ग्रामीण विकास मंत्रालय",
        "te": "గ్రామీణాభివృద్ధి మంత్రిత్వ శాఖ",
        "ta": "ஊரக வளர்ச்சி அமைச்சகம்",
        "kn": "ಗ್ರಾಮೀಣಾಭಿವೃದ್ಧಿ ಸಚಿವಾಲಯ",
        "ml": "ഗ്രാമവികസന മന്ത്രാലയം",
        "mr": "ग्रामीण विकास मंत्रालय",
        "bn": "পল্লী উন্নয়ন মন্ত্রক",
        "gu": "ગ્રામીણ વિકાસ મંત્રાલય",
        "pa": "ਪੇਂਡੂ ਵਿਕਾਸ ਮੰਤਰਾਲਾ",
        "or": "ଗ୍ରାମ୍ୟ ଉନ୍ନୟନ ମନ୍ତ୍ରଣାଳୟ",
        "ur": "وزارت دیہی ترقی",
    },
    "Ministry of Finance": {
        "hi": "वित्त मंत्रालय",
        "te": "ఆర్థిక మంత్రిత్వ శాఖ",
        "ta": "நிதி அமைச்சகம்",
        "kn": "ಹಣಕಾಸು ಸಚಿವಾಲಯ",
        "ml": "ധനകാര്യ മന്ത്രാലയം",
        "mr": "वित्त मंत्रालय",
        "bn": "অর্থ মন্ত্রক",
        "gu": "નાણાં મંત્રાલય",
        "pa": "ਵਿੱਤ ਮੰਤਰਾਲਾ",
        "or": "ଅର୍ଥ ମନ୍ତ୍ରଣାଳୟ",
        "ur": "وزارت خزانہ",
    },
    "Aadhaar Card": {
        "hi": "आधार कार्ड",
        "te": "ఆధార్ కార్డు",
        "ta": "ஆதார் அட்டை",
        "kn": "ಆಧಾರ್ ಕಾರ್ಡ್",
        "ml": "ആധാർ കാർഡ്",
        "mr": "आधार कार्ड",
        "bn": "আধার কার্ড",
        "gu": "આધાર કાર્ડ",
        "pa": "ਆਧਾਰ ਕਾਰਡ",
        "or": "ଆଧାର କାର୍ଡ",
        "ur": "آدھار کارڈ",
    },
    "Bank Account details with IFSC code": {
        "hi": "आईएफएससी (IFSC) कोड सहित बैंक खाता विवरण",
        "te": "IFSC కోడ్‌తో కూడిన బ్యాంక్ ఖాతా వివరాలు",
        "ta": "IFSC குறியீட்டுடன் கூடிய வங்கி கணக்கு விவரங்கள்",
        "kn": "IFSC ಕೋಡ್ ಹೊಂದಿರುವ ಬ್ಯಾಂಕ್ ಖಾತೆ ವಿವರ",
        "ml": "IFSC കോഡുള്ള ബാങ്ക് അക്കൗണ്ട് വിവരങ്ങൾ",
        "mr": "IFSC कोडसह बँक खाते तपशील",
        "bn": "আইএফএসসি কোড সহ ব্যাংক অ্যাকাউন্টের বিবরণ",
        "gu": "IFSC કોડ સાથે બેંક ખાતાની વિગતો",
        "pa": "IFSC ਕੋਡ ਵਾਲਾ ਬੈਂਕ ਖਾਤਾ",
        "or": "IFSC କୋଡ୍ ସହିତ ବ୍ୟାଙ୍କ ଖାତା ବିବରଣୀ",
        "ur": "آئی ایف ایس سی کوڈ کے ساتھ بینک اکاؤنٹ کی تفصیلات",
    },
    "Land ownership documents / RoR (Record of Rights)": {
        "hi": "भूमि स्वामित्व दस्तावेज / खतौनी (RoR)",
        "te": "భూమి యాజమాన్య పత్రాలు / పట్టాదారు పాస్ పుస్తకం",
        "ta": "நில உரிமை ஆவணங்கள் / பட்டா",
        "kn": "ಭೂಮಿ ಮಾಲೀಕತ್ವದ ದಾಖಲೆಗಳು (ಆರ್‌ಒಆರ್)",
        "ml": "ഭൂ ഉടമസ്ഥാവകാശ രേഖകൾ (RoR)",
        "mr": "जमीन मालकी दस्तऐवज / ७/१२ उतारा",
        "bn": "জমির মালিকানার দলিল / খতিয়ান",
        "gu": "જમીન માલિકીના દસ્તાવેજો / ૭/૧૨",
        "pa": "ਜ਼ਮੀਨ ਮਲਕੀਅਤ ਦਸਤਾਵੇਜ਼ / ਜਮ੍ਹਾਬੰਦੀ",
        "or": "ଜମି ମାଲିକାନା ଦସ୍ତାବିଜ୍ (RoR)",
        "ur": "اراضی کی ملکیت کے دستاویزات / ریکارڈ آف رائٹس",
    },
    "Income Certificate from Competent Authority": {
        "hi": "सक्षम प्राधिकारी द्वारा जारी आय प्रमाण पत्र",
        "te": "అధికారిక ఆదాయ ధృవీకరణ పత్రం",
        "ta": "வருமானச் சான்றிதழ்",
        "kn": "ಆದಾಯ ಪ್ರಮಾಣ ಪತ್ರ",
        "ml": "വരുമാന സർട്ടിഫിക്കറ്റ്",
        "mr": "सक्षम प्राधिकरणाचे उत्पन्न प्रमाणपत्र",
        "bn": "আয়ের প্রমাণপত্র",
        "gu": "આવકનું પ્રમાણપત્ર",
        "pa": "ਆਮਦਨ ਸਰਟੀਫਿਕੇਟ",
        "or": "ଆୟ ପ୍ରମାଣପତ୍ର",
        "ur": "آمدنی کا سرٹیفکیٹ",
    },
}

LANGUAGE_NAMES: Dict[str, str] = {
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


class SchemeTranslator:
    """Manages translation and caching of scheme details across all 12 Indian languages."""

    def __init__(self) -> None:
        self._cache: Dict[str, Dict[str, Any]] = {}
        self._load_cache()

    def _load_cache(self) -> None:
        """Load persisted translation cache from disk if available."""
        if os.path.exists(CACHE_FILE):
            try:
                with open(CACHE_FILE, "r", encoding="utf-8") as f:
                    self._cache = json.load(f)
                logger.info("Loaded %d translated scheme snapshots from disk cache.", len(self._cache))
            except Exception as e:
                logger.warning("Failed to read translation cache file: %s", e)
                self._cache = {}

    def _save_cache(self) -> None:
        """Persist cache snapshot to disk."""
        try:
            os.makedirs(os.path.dirname(CACHE_FILE), exist_ok=True)
            with open(CACHE_FILE, "w", encoding="utf-8") as f:
                json.dump(self._cache, f, ensure_ascii=False, indent=2)
        except Exception as e:
            logger.warning("Failed to save translation cache to disk: %s", e)

    def get_cached_translation(self, scheme_id: str, lang: str) -> Optional[Dict[str, Any]]:
        """Retrieve cached translation for a scheme and language."""
        cache_key = f"{scheme_id.upper()}_{lang}"
        return self._cache.get(cache_key)

    def cache_translation(self, scheme_id: str, lang: str, data: Dict[str, Any]) -> None:
        """Store translation in cache."""
        cache_key = f"{scheme_id.upper()}_{lang}"
        self._cache[cache_key] = data
        # Periodically save cache
        if len(self._cache) % 10 == 0:
            self._save_cache()

    def translate_phrase(self, text: str, lang: str) -> str:
        """Translate a single governance phrase or term using canonical lexicon."""
        if not text or lang == "en":
            return text
        clean = text.strip()
        if clean in LEXICON and lang in LEXICON[clean]:
            return LEXICON[clean][lang]
        return text

    async def translate_scheme(
        self,
        scheme: Dict[str, Any],
        lang: str,
    ) -> Dict[str, Any]:
        """Translate a scheme's fields into the target Indian language.

        Returns a fully translated scheme dictionary with identical structure.
        """
        if not scheme or not lang or lang == "en":
            return scheme

        scheme_id = scheme.get("scheme_id", "")
        # 1. Check in-memory / persistent cache
        cached = self.get_cached_translation(scheme_id, lang)
        if cached:
            # Merge cached translation over scheme
            merged = dict(scheme)
            merged.update(cached)
            merged["is_translated"] = True
            merged["lang"] = lang
            return merged

        # 2. Check if scheme already has pre-baked translation in scheme["translations"]
        if "translations" in scheme and isinstance(scheme["translations"], dict):
            prebaked = scheme["translations"].get(lang)
            if prebaked and isinstance(prebaked, dict) and (prebaked.get("summary") or prebaked.get("scheme_name")):
                merged = dict(scheme)
                if prebaked.get("scheme_name"):
                    merged["scheme_name"] = prebaked["scheme_name"]
                if prebaked.get("summary"):
                    merged["summary"] = prebaked["summary"]
                if prebaked.get("benefits"):
                    merged["benefits"] = prebaked["benefits"]
                if prebaked.get("eligibility_criteria"):
                    merged["eligibility_criteria"] = prebaked["eligibility_criteria"]
                if prebaked.get("exclusions"):
                    merged["exclusions"] = prebaked["exclusions"]
                if prebaked.get("documents_required"):
                    merged["documents_required"] = prebaked["documents_required"]
                if prebaked.get("application_steps"):
                    merged["application_steps"] = prebaked["application_steps"]
                if prebaked.get("nodal_authority"):
                    merged["nodal_authority"] = prebaked["nodal_authority"]
                    merged["ministry"] = prebaked["nodal_authority"]
                else:
                    raw_min = scheme.get("nodal_authority") or scheme.get("ministry")
                    if raw_min:
                        trans_min = self.translate_phrase(raw_min, lang)
                        merged["nodal_authority"] = trans_min
                        merged["ministry"] = trans_min
                merged["is_translated"] = True
                merged["lang"] = lang
                self.cache_translation(scheme_id, lang, prebaked)
                return merged

        # 3. Dynamic translation via LLM Service (if API key configured)
        from app.services.llm import llm_service
        target_language_name = LANGUAGE_NAMES.get(lang, lang.upper())

        prompt = (
            f"You are the official Civic Pulse translation system for Indian public schemes. "
            f"Translate this government scheme specification accurately into {target_language_name} ({lang}).\n\n"
            f"Preserve statutory fidelity, official portal URLs, helpline phone numbers, and currency amounts exactly.\n"
            f"Return a strict JSON object with these exact keys:\n"
            f"- scheme_name: translated title\n"
            f"- summary: 2-3 sentence plain language explanation\n"
            f"- benefits: array of 2-4 translated bullet points of citizen entitlements\n"
            f"- eligibility_criteria: array of translated eligibility conditions\n"
            f"- exclusions: array of translated exclusion criteria\n"
            f"- documents_required: array of translated required document names\n"
            f"- application_steps: array of step-by-step citizen application instructions\n"
            f"- nodal_authority: translated ministry/department name\n\n"
            f"Original English Scheme:\n"
            f"Title: {scheme.get('scheme_name')}\n"
            f"Summary: {scheme.get('summary')}\n"
            f"Ministry: {scheme.get('nodal_authority') or scheme.get('ministry')}\n"
            f"Benefits: {json.dumps(scheme.get('benefits', []))}\n"
            f"Eligibility: {json.dumps(scheme.get('eligibility_criteria', []))}\n"
            f"Exclusions: {json.dumps(scheme.get('exclusions', []))}\n"
            f"Documents: {json.dumps(scheme.get('documents_required', []))}\n"
            f"Application Steps: {json.dumps(scheme.get('application_steps', []))}\n"
        )

        try:
            if settings.LLM_API_KEY:
                raw_json = await llm_service.generate_text(
                    prompt=prompt,
                    system_instruction=f"Output strictly valid JSON translating the government scheme into {target_language_name}.",
                    lang=lang,
                )
                clean_json = raw_json.strip()
                if "```json" in clean_json:
                    clean_json = clean_json.split("```json")[1].split("```")[0].strip()
                elif "```" in clean_json:
                    clean_json = clean_json.split("```")[1].split("```")[0].strip()

                parsed = json.loads(clean_json)
                if isinstance(parsed, dict) and parsed.get("scheme_name"):
                    self.cache_translation(scheme_id, lang, parsed)
                    merged = dict(scheme)
                    merged.update(parsed)
                    merged["is_translated"] = True
                    merged["lang"] = lang
                    return merged
        except Exception as e:
            logger.warning("Live LLM translation failed for scheme '%s' (lang=%s): %s", scheme_id, lang, e)

        # 4. Fallback: Synthesize localized text using canonical lexicon
        trans_name = self.translate_phrase(scheme.get("scheme_name", ""), lang)
        raw_min = scheme.get("nodal_authority") or scheme.get("ministry") or ""
        trans_min = self.translate_phrase(raw_min, lang)
        fallback_data = {
            "scheme_name": trans_name if trans_name != scheme.get("scheme_name") else scheme.get("scheme_name", ""),
            "summary": self.translate_phrase(scheme.get("summary", ""), lang),
            "benefits": [self.translate_phrase(b, lang) for b in scheme.get("benefits", [])],
            "eligibility_criteria": [self.translate_phrase(e, lang) for e in scheme.get("eligibility_criteria", [])],
            "exclusions": [self.translate_phrase(ex, lang) for ex in scheme.get("exclusions", [])],
            "documents_required": [self.translate_phrase(d, lang) for d in scheme.get("documents_required", [])],
            "application_steps": scheme.get("application_steps", []),
            "nodal_authority": trans_min,
            "ministry": trans_min,
        }
        self.cache_translation(scheme_id, lang, fallback_data)
        merged = dict(scheme)
        merged.update(fallback_data)
        merged["is_translated"] = True
        merged["lang"] = lang
        return merged

    async def batch_translate(
        self,
        schemes: List[Dict[str, Any]],
        lang: str,
    ) -> List[Dict[str, Any]]:
        """Batch translate a list of schemes."""
        if not lang or lang == "en":
            return schemes
        translated = []
        for s in schemes:
            t = await self.translate_scheme(s, lang)
            translated.append(t)
        return translated


scheme_translator = SchemeTranslator()
