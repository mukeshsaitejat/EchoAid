"""
EchoAid — FastAPI application entry point.

Serves the frontend static files and mounts all API routers.
Run with:
    uvicorn backend.main:app --reload
"""

from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from backend.config import settings
from backend.database import init_db
from backend.routers import ai, auth, categories, health, keywords, preferences

# ---------------------------------------------------------------------------
# Lifespan
# ---------------------------------------------------------------------------


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


# ---------------------------------------------------------------------------
# Application
# ---------------------------------------------------------------------------

app = FastAPI(
    title="EchoAid",
    description="A personalized communication assistant for people with speech difficulties.",
    version="0.2.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    lifespan=lifespan,
)

# Allow same-origin requests (frontend served from FastAPI itself)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8000", "http://localhost:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------------------------
# API routers
# ---------------------------------------------------------------------------

app.include_router(health.router,       prefix="/api")
app.include_router(auth.router,         prefix="/api")
app.include_router(categories.router,   prefix="/api")
app.include_router(keywords.router,     prefix="/api")
app.include_router(preferences.router,  prefix="/api")
app.include_router(ai.router,           prefix="/api")

# ---------------------------------------------------------------------------
# Frontend static files
# ---------------------------------------------------------------------------

FRONTEND_DIR = Path(__file__).parent.parent / "frontend"
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# ---------------------------------------------------------------------------
# Frontend page routes
# ---------------------------------------------------------------------------


@app.get("/test", include_in_schema=False)
def serve_test() -> FileResponse:
    """Simple test page to verify server connectivity."""
    return FileResponse(str(FRONTEND_DIR / "test.html"))


@app.get("/", include_in_schema=False)
def serve_index() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "index.html"))


@app.get("/patient", include_in_schema=False)
def serve_patient() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "patient.html"))


@app.get("/guardian", include_in_schema=False)
def serve_guardian() -> FileResponse:
    return FileResponse(str(FRONTEND_DIR / "guardian.html"))
