"""
EchoAid — FastAPI application entry point.

Serves the frontend static files and mounts all API routers.
Run with:
    uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routers import health

# ---------------------------------------------------------------------------
# Lifespan: initialize database on startup
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Create database tables on first run (idempotent), then yield."""
    init_db()
    yield


# ---------------------------------------------------------------------------
# Application instance
# ---------------------------------------------------------------------------

app = FastAPI(
    title="EchoAid",
    description="A personalized communication assistant for people with speech difficulties.",
    version="0.1.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)


# ---------------------------------------------------------------------------
# API routers
# ---------------------------------------------------------------------------

app.include_router(health.router, prefix="/api")

# Phase 2 routers will be added here:
# app.include_router(categories.router, prefix="/api")
# app.include_router(keywords.router, prefix="/api")

# ---------------------------------------------------------------------------
# Frontend static files
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"

# Mount CSS, JS, and other assets under /static
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")


# ---------------------------------------------------------------------------
# Frontend page routes
# ---------------------------------------------------------------------------


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    """Serve the application shell (mode selector)."""
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/patient", include_in_schema=False)
def serve_patient() -> FileResponse:
    """Serve the Patient Mode interface."""
    return FileResponse(str(FRONTEND_DIR / "patient.html"))


@app.get("/guardian", include_in_schema=False)
def serve_guardian() -> FileResponse:
    """Serve the Guardian Mode interface."""
    return FileResponse(str(FRONTEND_DIR / "guardian.html"))
