"""
Health-check router.

GET /health — returns application status, version, and environment.
"""

from fastapi import APIRouter

from backend.config import settings
from backend.schemas import HealthResponse

router = APIRouter(tags=["Health"])

APP_VERSION = "0.1.0"


@router.get("/health", response_model=HealthResponse, summary="Health check")
def health_check() -> HealthResponse:
    """
    Returns a simple status payload.
    Use this endpoint to verify the backend is running and reachable.
    """
    return HealthResponse(
        status="ok",
        version=APP_VERSION,
        environment=settings.app_env,
    )
