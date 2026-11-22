"""Civic_AI API Routers Package."""

from app.api.explain import router as explain_router
from app.api.eligibility import router as eligibility_router
from app.api.rights import router as rights_router
from app.api.verify import router as verify_router
from app.api.states import router as states_router

__all__ = [
    "explain_router",
    "eligibility_router",
    "rights_router",
    "verify_router",
    "states_router",
]
