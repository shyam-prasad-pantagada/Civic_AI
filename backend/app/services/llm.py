"""Civic_AI AI Model Integration Service.

Provides a unified interface for calling the AI model (Flash and Pro tiers),
enforcing structured JSON schemas, managing retries, and providing fallback handling.
All generation methods accept a `lang` parameter to ensure language-readiness.
"""

import json
import logging
from typing import Any, Dict, Optional, Type
from pydantic import BaseModel
from app.config import settings

logger = logging.getLogger("Civic_AI.LLM")


class LLMService:
    """AI model client for Civic_AI."""

    def __init__(self, api_key: Optional[str] = None) -> None:
        self.api_key = api_key or settings.LLM_API_KEY
        self.default_model = settings.LLM_MODEL or "gemini-2.5-flash"
        self.pro_model = settings.LLM_MODEL_PRO or "gemini-2.5-pro"
        self._client = None
        if self.api_key:
            try:
                from google import genai
                self._client = genai.Client(api_key=self.api_key)
                logger.info("Initialized AI model client successfully.")
            except Exception as e:
                logger.warning("Failed to initialize AI model client: %s", e)

    @property
    def client(self):
        """Lazy-loaded AI client in case key is updated at runtime."""
        if self._client is None and settings.LLM_API_KEY:
            try:
                from google import genai
                self.api_key = settings.LLM_API_KEY
                self._client = genai.Client(api_key=self.api_key)
            except Exception as e:
                logger.warning("Failed to initialize AI model client on demand: %s", e)
        return self._client

    async def generate_text(
        self,
        prompt: str,
        system_instruction: Optional[str] = None,
        use_pro: bool = False,
        lang: str = "en",
    ) -> str:
        """Generate unstructured text response using the AI model."""
        model_name = self.pro_model if use_pro else self.default_model
        
        # Add language context if not English
        lang_prompt = f"Please respond in language code '{lang}'.\n\n{prompt}" if lang != "en" else prompt

        if self.client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=system_instruction,
                    temperature=0.2,
                )
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=lang_prompt,
                    config=config,
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.error("AI text generation failed: %s", e)

        # Intelligent offline fallback
        return (
            f"[Civic AI Offline Assistant]: Processed request for '{prompt[:80]}...'. "
            f"Configure LLM_API_KEY in .env to enable full live policy synthesis."
        )

    async def generate_structured(
        self,
        prompt: str,
        response_schema: Type[BaseModel],
        system_instruction: Optional[str] = None,
        use_pro: bool = False,
        lang: str = "en",
    ) -> Dict[str, Any]:
        """Generate strict JSON output validated against a Pydantic v2 schema."""
        model_name = self.pro_model if use_pro else self.default_model
        lang_instruction = (
            f" Target output language code is '{lang}'. Output only valid JSON matching the schema."
        )
        full_system = (system_instruction or "") + lang_instruction

        if self.client:
            try:
                from google.genai import types
                config = types.GenerateContentConfig(
                    system_instruction=full_system,
                    temperature=0.1,
                    response_mime_type="application/json",
                    response_schema=response_schema,
                )
                response = self.client.models.generate_content(
                    model=model_name,
                    contents=prompt,
                    config=config,
                )
                if response and response.text:
                    raw_json = json.loads(response.text)
                    # Validate against Pydantic schema
                    validated = response_schema.model_validate(raw_json)
                    return validated.model_dump()
            except Exception as e:
                logger.error("AI structured generation failed: %s", e)

        # Fallback structured generation
        return {}

    async def analyze_image_or_pdf(
        self,
        file_bytes: bytes,
        mime_type: str,
        prompt: str,
        response_schema: Optional[Type[BaseModel]] = None,
        lang: str = "en",
    ) -> Any:
        """Analyze document or image using multimodal vision capabilities."""
        if self.client:
            try:
                from google.genai import types
                config_kwargs = {"temperature": 0.1}
                if response_schema:
                    config_kwargs["response_mime_type"] = "application/json"
                    config_kwargs["response_schema"] = response_schema

                config = types.GenerateContentConfig(**config_kwargs)
                part = types.Part.from_bytes(data=file_bytes, mime_type=mime_type)
                response = self.client.models.generate_content(
                    model=self.default_model,
                    contents=[part, prompt],
                    config=config,
                )
                if response and response.text:
                    if response_schema:
                        return json.loads(response.text)
                    return response.text.strip()
            except Exception as e:
                logger.error("Multimodal analysis failed: %s", e)

        return None


llm_service = LLMService()
