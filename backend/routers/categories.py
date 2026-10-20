"""
Category management router.

All mutating endpoints require guardian authentication.
GET endpoints are public so Patient Mode can read categories.
"""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from backend.auth import require_guardian
from backend.database import get_db
from backend.models import Category, Keyword
from backend.schemas import CategoryCreate, CategoryResponse, CategoryUpdate, CategoryWithKeywords

router = APIRouter(prefix="/categories", tags=["Categories"])


# ──────────────────────────────────────────────────────────────────────
# Public — Patient Mode reads these
# ──────────────────────────────────────────────────────────────────────


@router.get("/", response_model=list[CategoryResponse])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    """Return all enabled categories ordered by display_order."""
    return (
        db.query(Category)
        .filter(Category.is_enabled == True)  # noqa: E712
        .order_by(Category.display_order, Category.name)
        .all()
    )


@router.get("/all", response_model=list[CategoryResponse],
            dependencies=[Depends(require_guardian)])
def list_all_categories(db: Session = Depends(get_db)) -> list[Category]:
    """Guardian only — return all categories including disabled ones."""
    return (
        db.query(Category)
        .order_by(Category.display_order, Category.name)
        .all()
    )


@router.get("/{category_id}", response_model=CategoryWithKeywords)
def get_category(category_id: int, db: Session = Depends(get_db)) -> Category:
    """Return a single category with its enabled keywords."""
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")
    return cat


# ──────────────────────────────────────────────────────────────────────
# Guardian only
# ──────────────────────────────────────────────────────────────────────


@router.post("/", response_model=CategoryResponse, status_code=201,
             dependencies=[Depends(require_guardian)])
def create_category(body: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    """Create a new category."""
    existing = db.query(Category).filter(Category.name == body.name).first()
    if existing:
        raise HTTPException(status_code=409, detail="A category with that name already exists.")

    cat = Category(**body.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.patch("/{category_id}", response_model=CategoryResponse,
              dependencies=[Depends(require_guardian)])
def update_category(
    category_id: int, body: CategoryUpdate, db: Session = Depends(get_db)
) -> Category:
    """Update an existing category."""
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")

    updates = body.model_dump(exclude_unset=True)
    for field, value in updates.items():
        setattr(cat, field, value)

    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{category_id}", status_code=204,
               dependencies=[Depends(require_guardian)])
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    """
    Delete a category.  Fails if the category still has keywords —
    the guardian must reassign or delete them first.
    """
    cat = db.get(Category, category_id)
    if not cat:
        raise HTTPException(status_code=404, detail="Category not found.")

    keyword_count = db.query(Keyword).filter(Keyword.category_id == category_id).count()
    if keyword_count > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Cannot delete: {keyword_count} keyword(s) still belong to this category. "
                   "Reassign or delete them first.",
        )

    db.delete(cat)
    db.commit()
