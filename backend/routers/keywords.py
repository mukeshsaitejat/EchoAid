"""
Keyword management router.

GET  /api/keywords/          — public (Patient Mode)
GET  /api/keywords/urgent    — public (Patient Mode urgent panel)
POST /api/keywords/          — guardian only
PATCH/DELETE                 — guardian only
POST /api/keywords/seed      — guardian only (seed sample phrases)
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import require_guardian
from backend.database import get_db
from backend.models import Category, Keyword
from backend.schemas import KeywordCreate, KeywordResponse, KeywordUpdate

router = APIRouter(prefix="/keywords", tags=["Keywords"])


# ──────────────────────────────────────────────────────────────────────
# Public
# ──────────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[KeywordResponse])
def list_keywords(
    category_id: int | None = None,
    db: Session = Depends(get_db),
) -> list[Keyword]:
    """Return all enabled keywords, optionally filtered by category."""
    q = db.query(Keyword).filter(Keyword.is_enabled == True)  # noqa: E712
    if category_id is not None:
        q = q.filter(Keyword.category_id == category_id)
    return q.order_by(Keyword.display_order, Keyword.label).all()


@router.get("/urgent", response_model=list[KeywordResponse])
def list_urgent_keywords(db: Session = Depends(get_db)) -> list[Keyword]:
    """Return all enabled urgent keywords."""
    return (
        db.query(Keyword)
        .filter(Keyword.is_urgent == True, Keyword.is_enabled == True)  # noqa: E712
        .order_by(Keyword.display_order, Keyword.label)
        .all()
    )


@router.get("/all", response_model=list[KeywordResponse],
            dependencies=[Depends(require_guardian)])
def list_all_keywords(db: Session = Depends(get_db)) -> list[Keyword]:
    """Guardian only — all keywords including disabled."""
    return db.query(Keyword).order_by(Keyword.display_order, Keyword.label).all()


@router.get("/{keyword_id}", response_model=KeywordResponse)
def get_keyword(keyword_id: int, db: Session = Depends(get_db)) -> Keyword:
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found.")
    return kw


# ──────────────────────────────────────────────────────────────────────
# Guardian only
# ──────────────────────────────────────────────────────────────────────


@router.post("/", response_model=KeywordResponse, status_code=201,
             dependencies=[Depends(require_guardian)])
def create_keyword(body: KeywordCreate, db: Session = Depends(get_db)) -> Keyword:
    """Create a new keyword."""
    if body.category_id is not None:
        cat = db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found.")

    kw = Keyword(**body.model_dump())
    db.add(kw)
    db.commit()
    db.refresh(kw)
    return kw


@router.patch("/{keyword_id}", response_model=KeywordResponse,
              dependencies=[Depends(require_guardian)])
def update_keyword(
    keyword_id: int, body: KeywordUpdate, db: Session = Depends(get_db)
) -> Keyword:
    """Update a keyword's fields."""
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found.")

    if body.category_id is not None:
        cat = db.get(Category, body.category_id)
        if not cat:
            raise HTTPException(status_code=404, detail="Category not found.")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(kw, field, value)

    db.commit()
    db.refresh(kw)
    return kw


@router.delete("/{keyword_id}", status_code=204,
               dependencies=[Depends(require_guardian)])
def delete_keyword(keyword_id: int, db: Session = Depends(get_db)) -> None:
    kw = db.get(Keyword, keyword_id)
    if not kw:
        raise HTTPException(status_code=404, detail="Keyword not found.")
    db.delete(kw)
    db.commit()


@router.post("/seed", status_code=201,
             dependencies=[Depends(require_guardian)])
def seed_sample_phrases(db: Session = Depends(get_db)) -> dict:
    """
    Seed initial sample categories and phrases.
    Safe to call multiple times — skips categories/keywords that already exist by name.
    """
    SEED_DATA = [
        {
            "category": {"name": "Urgent", "icon": "🚨", "display_order": 0},
            "keywords": [
                {"label": "Help", "message": "Please help me.", "is_urgent": True, "icon": "🆘", "display_order": 0},
                {"label": "Stop", "message": "Stop, please.", "is_urgent": True, "icon": "✋", "display_order": 1},
                {"label": "Wait", "message": "Please wait.", "is_urgent": True, "icon": "⏳", "display_order": 2},
                {"label": "No", "message": "I do not want that.", "is_urgent": True, "icon": "❌", "display_order": 3},
                {"label": "More time", "message": "Please give me more time.", "is_urgent": False, "icon": "🕐", "display_order": 4},
                {"label": "Privacy", "message": "I need some privacy.", "is_urgent": False, "icon": "🔒", "display_order": 5},
            ],
        },
        {
            "category": {"name": "Daily Needs", "icon": "🏠", "display_order": 1},
            "keywords": [
                {"label": "Water", "message": "I would like some water, please.", "icon": "💧", "display_order": 0},
                {"label": "Food", "message": "I am hungry. Can I have something to eat?", "icon": "🍽️", "display_order": 1},
                {"label": "Bathroom", "message": "I need to use the bathroom.", "icon": "🚻", "display_order": 2},
                {"label": "Rest", "message": "I need to rest.", "icon": "😴", "display_order": 3},
                {"label": "Blanket", "message": "Could I have a blanket, please?", "icon": "🛏️", "display_order": 4},
                {"label": "Cold", "message": "I am feeling cold.", "icon": "🥶", "display_order": 5},
                {"label": "Hot", "message": "I am feeling too warm.", "icon": "🥵", "display_order": 6},
            ],
        },
        {
            "category": {"name": "Health", "icon": "❤️", "display_order": 2},
            "keywords": [
                {"label": "Pain", "message": "I am in pain. Please help.", "is_urgent": True, "icon": "😣", "display_order": 0},
                {"label": "Medicine", "message": "I need my medicine.", "icon": "💊", "display_order": 1},
                {"label": "Dizzy", "message": "I feel dizzy.", "icon": "😵", "display_order": 2},
                {"label": "Nausea", "message": "I feel nauseous.", "icon": "🤢", "display_order": 3},
                {"label": "Doctor", "message": "I would like to see the doctor.", "is_urgent": True, "icon": "🩺", "display_order": 4},
            ],
        },
        {
            "category": {"name": "Emotions", "icon": "😊", "display_order": 3},
            "keywords": [
                {"label": "Happy", "message": "I am feeling happy.", "icon": "😊", "display_order": 0},
                {"label": "Sad", "message": "I am feeling sad.", "icon": "😢", "display_order": 1},
                {"label": "Anxious", "message": "I am feeling anxious.", "icon": "😰", "display_order": 2},
                {"label": "Tired", "message": "I am very tired.", "icon": "😩", "display_order": 3},
                {"label": "OK", "message": "I am doing okay, thank you.", "icon": "👍", "display_order": 4},
                {"label": "Thank you", "message": "Thank you very much.", "icon": "🙏", "display_order": 5},
            ],
        },
        {
            "category": {"name": "People", "icon": "👥", "display_order": 4},
            "keywords": [
                {"label": "Family", "message": "I would like to see my family.", "icon": "👨‍👩‍👧", "display_order": 0},
                {"label": "Nurse", "message": "Can you call the nurse, please?", "icon": "👩‍⚕️", "display_order": 1},
                {"label": "Alone", "message": "I would like to be alone for a while.", "icon": "🧘", "display_order": 2},
                {"label": "Phone", "message": "I need to make a phone call.", "icon": "📱", "display_order": 3},
            ],
        },
    ]

    created_categories = 0
    created_keywords = 0

    for block in SEED_DATA:
        cat_data = block["category"]
        cat = db.query(Category).filter(Category.name == cat_data["name"]).first()
        if not cat:
            cat = Category(**cat_data)
            db.add(cat)
            db.flush()
            created_categories += 1

        for kw_data in block["keywords"]:
            existing = (
                db.query(Keyword)
                .filter(Keyword.label == kw_data["label"], Keyword.category_id == cat.id)
                .first()
            )
            if not existing:
                kw = Keyword(category_id=cat.id, **kw_data)
                db.add(kw)
                created_keywords += 1

    db.commit()
    return {
        "message": "Seed complete.",
        "categories_created": created_categories,
        "keywords_created": created_keywords,
    }
