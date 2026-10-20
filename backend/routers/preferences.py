"""
Communication preferences router.

GET  /api/preferences  — public (Patient Mode reads on startup)
PATCH /api/preferences — guardian only
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.auth import require_guardian
from backend.database import get_db
from backend.models import CommunicationPreference
from backend.schemas import PreferencesResponse, PreferencesUpdate

router = APIRouter(prefix="/preferences", tags=["Preferences"])


def _get_or_create_prefs(db: Session) -> CommunicationPreference:
    """Return the default preference row, creating it if it does not exist."""
    prefs = db.query(CommunicationPreference).filter_by(profile_name="default").first()
    if not prefs:
        prefs = CommunicationPreference(profile_name="default")
        db.add(prefs)
        db.commit()
        db.refresh(prefs)
    return prefs


@router.get("/", response_model=PreferencesResponse)
def get_preferences(db: Session = Depends(get_db)) -> CommunicationPreference:
    return _get_or_create_prefs(db)


@router.patch("/", response_model=PreferencesResponse,
              dependencies=[Depends(require_guardian)])
def update_preferences(
    body: PreferencesUpdate, db: Session = Depends(get_db)
) -> CommunicationPreference:
    prefs = _get_or_create_prefs(db)
    for field, value in body.model_dump(exclude_unset=True).items():
        setattr(prefs, field, value)
    db.commit()
    db.refresh(prefs)
    return prefs
