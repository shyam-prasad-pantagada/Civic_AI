"""Civic_AI Main FastAPI Application.

Phase 0 bootstrap with CORS, Lifespan configuration, /health endpoint,
and API routers for notice explainer, scheme eligibility, citizen rights,
voice synthesis/transcription, live verification, and state coverage.
"""

from contextlib import asynccontextmanager
import logging
from typing import Any, AsyncGenerator, Dict

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.eligibility import router as eligibility_router
from app.api.explain import router as explain_router
from app.api.rights import router as rights_router
from app.api.states import router as states_router
from app.api.stats import router as stats_router
from app.api.verify import router as verify_router
from app.config import settings

logger = logging.getLogger("Civic_AI")
logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """Lifespan context manager that initializes configs and services on startup."""
    logger.info("Starting %s v%s...", settings.APP_NAME, settings.APP_VERSION)
    # Ensure YAML configs are loaded
    settings.load_yaml_configs()
    logger.info("Enabled languages: %s", settings.get_enabled_languages())
    logger.info("Pilot states: %s", settings.get_pilot_states())
    logger.info("%s ready to serve requests.", settings.APP_NAME)
    yield
    logger.info("Shutting down %s...", settings.APP_NAME)


app = FastAPI(
    title="Civic_AI",
    description="Multilingual Policy, Rights & Scheme Explainer for India",
    version="0.1.0",
    lifespan=lifespan,
)

# CORS Middleware setup - Tightened to known local origins and configured API host
allowed_origins = [
    "http://localhost:3000",
    "http://127.0.0.1:3000",
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5174",
]
if settings.VITE_API_URL and settings.VITE_API_URL not in allowed_origins:
    allowed_origins.append(settings.VITE_API_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["system"])
async def health_check() -> Dict[str, str]:
    """Health check endpoint for container probes and monitoring."""
    return {
        "status": "ok",
        "app": "Civic_AI",
        "version": "0.1.0",
    }


# Include API Routers under /api prefix
app.include_router(explain_router, prefix="/api")
app.include_router(eligibility_router, prefix="/api")
app.include_router(rights_router, prefix="/api")
app.include_router(stats_router, prefix="/api")
app.include_router(verify_router, prefix="/api")
app.include_router(states_router, prefix="/api")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
