"""
EchoAid Pydantic schemas.

Defines request and response shapes for all API endpoints.
Schemas for later phases are included here so the structure is established early.
"""

from __future__ import annotations

import datetime
from typing import List, Optional

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


class HealthResponse(BaseModel):
    status: str
    version: str
    environment: str


# ---------------------------------------------------------------------------
# Category
# ---------------------------------------------------------------------------


class CategoryBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    display_order: int = Field(0, ge=0)
    is_enabled: bool = True

    @field_validator("name")
    @classmethod
    def name_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Category name must not be blank.")
        return v.strip()


class CategoryCreate(CategoryBase):
    pass


class CategoryUpdate(BaseModel):
    name: Optional[str] = Field(None, min_length=1, max_length=100)
    description: Optional[str] = Field(None, max_length=255)
    icon: Optional[str] = Field(None, max_length=100)
    display_order: Optional[int] = Field(None, ge=0)
    is_enabled: Optional[bool] = None


class CategoryResponse(CategoryBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Keyword
# ---------------------------------------------------------------------------


class KeywordBase(BaseModel):
    label: str = Field(..., min_length=1, max_length=100)
    message: str = Field(..., min_length=1)
    icon: Optional[str] = Field(None, max_length=100)
    is_urgent: bool = False
    is_enabled: bool = True
    display_order: int = Field(0, ge=0)
    category_id: Optional[int] = None

    @field_validator("label")
    @classmethod
    def label_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Keyword label must not be blank.")
        return v.strip()

    @field_validator("message")
    @classmethod
    def message_not_blank(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("Keyword message must not be blank.")
        return v.strip()


class KeywordCreate(KeywordBase):
    pass


class KeywordUpdate(BaseModel):
    label: Optional[str] = Field(None, min_length=1, max_length=100)
    message: Optional[str] = Field(None, min_length=1)
    icon: Optional[str] = Field(None, max_length=100)
    is_urgent: Optional[bool] = None
    is_enabled: Optional[bool] = None
    display_order: Optional[int] = Field(None, ge=0)
    category_id: Optional[int] = None


class KeywordResponse(KeywordBase):
    id: int
    created_at: datetime.datetime
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Category with nested keywords
# ---------------------------------------------------------------------------


class CategoryWithKeywords(CategoryResponse):
    keywords: List[KeywordResponse] = []

    model_config = {"from_attributes": True}


# ---------------------------------------------------------------------------
# Communication Preferences
# ---------------------------------------------------------------------------


class PreferencesUpdate(BaseModel):
    speech_rate: Optional[int] = Field(None, ge=50, le=200)
    speech_pitch: Optional[int] = Field(None, ge=50, le=200)
    preferred_voice: Optional[str] = Field(None, max_length=200)
    large_text: Optional[bool] = None
    high_contrast: Optional[bool] = None
    speak_on_select: Optional[bool] = None


class PreferencesResponse(BaseModel):
    id: int
    profile_name: str
    speech_rate: int
    speech_pitch: int
    preferred_voice: Optional[str]
    large_text: bool
    high_contrast: bool
    speak_on_select: bool
    updated_at: datetime.datetime

    model_config = {"from_attributes": True}
