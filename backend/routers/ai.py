"""
AI suggestion router.

POST /api/ai/suggest — generate candidate sentences from word fragments
GET  /api/ai/status  — check whether the AI provider is configured
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from backend.ai_service import (
    AINotConfiguredError,
    AIServiceError,
    generate_suggestions,
)
from backend.config import settings

router = APIRouter(prefix="/ai", tags=["AI"])


class SuggestRequest(BaseModel):
    fragments: str = Field(..., min_length=1, max_length=500,
                           description="Word fragments separated by commas or + signs.")


class SuggestResponse(BaseModel):
    suggestions: list[str]
    model: str
    fragments_received: str


class AIStatusResponse(BaseModel):
    configured: bool
    model: str
    message: str


@router.get("/status", response_model=AIStatusResponse)
def ai_status() -> AIStatusResponse:
    """Return whether the AI provider is configured."""
    if settings.ai_configured:
        return AIStatusResponse(
            configured=True,
            model=settings.ai_model,
            message=f"AI provider ready — model: {settings.ai_model}",
        )
    return AIStatusResponse(
        configured=False,
        model=settings.ai_model,
        message="AI provider not configured. Set AI_API_KEY in .env to enable.",
    )


@router.post("/suggest", response_model=SuggestResponse)
async def suggest(body: SuggestRequest) -> SuggestResponse:
    """
    Generate candidate sentences from user-supplied word fragments.

    The AI service is optional.  If not configured, returns a 503 with
    an honest status message so the frontend can fall back gracefully.
    """
    try:
        suggestions = await generate_suggestions(body.fragments)
    except AINotConfiguredError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=str(exc),
        )
    except AIServiceError as exc:
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail=str(exc),
        )

    return SuggestResponse(
        suggestions=suggestions,
        model=settings.ai_model,
        fragments_received=body.fragments,
    )
