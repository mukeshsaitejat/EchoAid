"""
EchoAid SQLAlchemy ORM models.

These models define the full eventual schema so that subsequent phases
do not require architectural changes.  Columns introduced in later phases
are already present but may not be used by Phase 1 routes.
"""

import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import relationship

from backend.database import Base


def _now() -> datetime.datetime:
    return datetime.datetime.now(datetime.timezone.utc).replace(tzinfo=None)


class Category(Base):
    """
    A grouping for keywords (e.g. Daily Needs, Health, Emotions).
    Guardians can create, rename, and delete categories.
    """

    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(String(255), nullable=True)
    icon = Column(String(100), nullable=True)   # optional emoji or SVG identifier
    display_order = Column(Integer, nullable=False, default=0)
    is_enabled = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    keywords = relationship(
        "Keyword",
        back_populates="category",
        cascade="all, delete-orphan",
        order_by="Keyword.display_order",
    )

    def __repr__(self) -> str:
        return f"<Category id={self.id} name={self.name!r}>"


class Keyword(Base):
    """
    A communication keyword button shown in Patient Mode.

    Each keyword has a short label (displayed on the button) and a full
    message (spoken or displayed when the keyword is selected).
    """

    __tablename__ = "keywords"

    id = Column(Integer, primary_key=True, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=True, index=True)

    # Button label shown in Patient Mode
    label = Column(String(100), nullable=False)

    # Full message spoken or displayed when this keyword is activated
    message = Column(Text, nullable=False)

    # Optional visual cue (emoji, icon name, or inline SVG key)
    icon = Column(String(100), nullable=True)

    # Urgency flag — urgent keywords are always surfaced in Patient Mode
    is_urgent = Column(Boolean, nullable=False, default=False)

    # Enabled keywords appear in Patient Mode; disabled ones are hidden
    is_enabled = Column(Boolean, nullable=False, default=True)

    # Ordering within a category
    display_order = Column(Integer, nullable=False, default=0)

    created_at = Column(DateTime, nullable=False, default=_now)
    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    category = relationship("Category", back_populates="keywords")

    def __repr__(self) -> str:
        return f"<Keyword id={self.id} label={self.label!r}>"


class CommunicationPreference(Base):
    """
    Per-profile communication preferences (Phase 3).

    A single row is used for the initial single-profile prototype.
    The schema is prepared now so Phase 3 does not require migrations.
    """

    __tablename__ = "communication_preferences"

    id = Column(Integer, primary_key=True, index=True)
    profile_name = Column(String(100), nullable=False, default="default")

    # Text-to-speech
    speech_rate = Column(Integer, nullable=False, default=100)    # percentage, 50–200
    speech_pitch = Column(Integer, nullable=False, default=100)   # percentage, 50–200
    preferred_voice = Column(String(200), nullable=True)

    # Display
    large_text = Column(Boolean, nullable=False, default=False)
    high_contrast = Column(Boolean, nullable=False, default=False)

    # Behaviour
    speak_on_select = Column(Boolean, nullable=False, default=False)

    updated_at = Column(DateTime, nullable=False, default=_now, onupdate=_now)

    def __repr__(self) -> str:
        return f"<CommunicationPreference profile={self.profile_name!r}>"
