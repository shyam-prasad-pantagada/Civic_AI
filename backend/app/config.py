"""Civic_AI Configuration Module.

Loads configuration from environment variables, .env file,
and YAML configuration files (languages.yaml, allowed_domains.yaml).
"""

from functools import lru_cache
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from ruamel.yaml import YAML
from pydantic import BaseModel, Field

_yaml = YAML()
_yaml.preserve_quotes = True

# Determine project roots
APP_DIR = Path(__file__).resolve().parent
BACKEND_DIR = APP_DIR.parent
PROJECT_ROOT = BACKEND_DIR.parent

# Attempt to load .env from project root or backend dir
try:
    from dotenv import load_dotenv

    for env_path in [
        PROJECT_ROOT / ".env",
        BACKEND_DIR / ".env",
        Path(".env"),
        PROJECT_ROOT / ".env.example",
    ]:
        if env_path.exists():
            load_dotenv(dotenv_path=env_path)
            break
except ImportError:
    pass


def find_config_dir() -> Path:
    """Locate config directory across various deployment environments."""
    env_config = os.getenv("CIVIC_AI_CONFIG_DIR")
    if env_config and Path(env_config).exists():
        return Path(env_config)

    candidates = [
        PROJECT_ROOT / "config",
        BACKEND_DIR / "config",
        Path("/config"),
        Path("config"),
    ]
    for candidate in candidates:
        if candidate.exists() and candidate.is_dir():
            return candidate
    return PROJECT_ROOT / "config"


class Settings(BaseModel):
    """Civic_AI Application Settings."""

    # Project identification
    APP_NAME: str = "Civic_AI"
    APP_VERSION: str = "0.1.0"

    # AI Models & Credentials
    LLM_API_KEY: str = Field(
        default_factory=lambda: os.getenv("LLM_API_KEY") or os.getenv("GEMINI_API_KEY", "")
    )
    LLM_MODEL: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL") or os.getenv("GEMINI_MODEL", "gemini-2.5-flash")
    )
    LLM_MODEL_PRO: str = Field(
        default_factory=lambda: os.getenv("LLM_MODEL_PRO") or os.getenv("GEMINI_MODEL_PRO", "gemini-2.5-pro")
    )

    # Search & Verification API Key
    TAVILY_API_KEY: str = Field(
        default_factory=lambda: os.getenv("TAVILY_API_KEY", "")
    )

    # Localization & Pilot States
    DEFAULT_LANG: str = "en"
    ENABLED_LANGS: str = "en"
    PILOT_STATES: str = "DL,MH,KA"

    # Limits & Frontend URL
    MAX_UPLOAD_MB: int = Field(
        default_factory=lambda: int(os.getenv("MAX_UPLOAD_MB", "50"))
    )
    MAX_PAGES: int = Field(
        default_factory=lambda: int(os.getenv("MAX_PAGES", "100"))
    )
    VITE_API_URL: str = Field(
        default_factory=lambda: os.getenv("VITE_API_URL", "http://localhost:8000")
    )

    # Backward compatibility properties
    @property
    def GEMINI_API_KEY(self) -> str:
        return self.LLM_API_KEY

    @property
    def GEMINI_MODEL(self) -> str:
        return self.LLM_MODEL

    @property
    def GEMINI_MODEL_PRO(self) -> str:
        return self.LLM_MODEL_PRO

    # Loaded Configurations from YAML
    languages_config: Dict[str, Any] = Field(default_factory=dict)
    allowed_domains_config: Dict[str, Any] = Field(default_factory=dict)

    def load_yaml_configs(self) -> None:
        """Load external YAML config files."""
        config_dir = find_config_dir()

        lang_file = config_dir / "languages.yaml"
        if lang_file.exists():
            try:
                with open(lang_file, "r", encoding="utf-8") as f:
                    data = dict(_yaml.load(f) or {})
                    self.languages_config = data.get("languages", {})
            except Exception:
                self.languages_config = {}
        else:
            self.languages_config = {
                "en": {
                    "name": "English",
                    "enabled": True,
                }
            }

        domains_file = config_dir / "allowed_domains.yaml"
        if domains_file.exists():
            try:
                with open(domains_file, "r", encoding="utf-8") as f:
                    self.allowed_domains_config = dict(_yaml.load(f) or {})
            except Exception:
                self.allowed_domains_config = {}
        else:
            self.allowed_domains_config = {
                "allowed_patterns": ["*.gov.in", "*.nic.in"],
            }

    def get_enabled_languages(self) -> List[str]:
        """Return list of enabled language codes."""
        if self.languages_config:
            yaml_enabled = [
                code
                for code, info in self.languages_config.items()
                if isinstance(info, dict) and info.get("enabled", False)
            ]
            if yaml_enabled:
                return yaml_enabled
        return ["en"]

    def is_language_supported(self, lang: str) -> bool:
        """Check whether a given language code is currently enabled."""
        if not lang:
            return False
        return lang.strip().lower() in self.get_enabled_languages()

    def get_language_info(self, lang: str) -> Optional[Dict[str, Any]]:
        """Return metadata for a language code."""
        return self.languages_config.get(lang.strip().lower())

    def get_pilot_states(self) -> List[str]:
        """Return list of uppercase pilot state codes."""
        return [s.strip().upper() for s in self.PILOT_STATES.split(",") if s.strip()]

    def get_allowed_domains(self) -> List[str]:
        """Return list of allowed domain patterns."""
        return self.allowed_domains_config.get("allowed_patterns", ["*.gov.in", "*.nic.in"])


@lru_cache()
def get_settings() -> Settings:
    """Cached singleton Settings provider for Civic_AI."""
    s = Settings()
    s.load_yaml_configs()
    return s


settings = get_settings()
