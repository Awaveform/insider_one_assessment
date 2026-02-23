"""Pydantic models representing the Petstore API contract.

Pure data models — no pytest, no test utilities.
Import from anywhere: tests, load scripts, future integrations.
"""

from __future__ import annotations

import logging
from typing import Any

from pydantic import BaseModel, field_validator

from models.enums import PetStatus

logger = logging.getLogger(__name__)


class Category(BaseModel):
    id: int | None = None
    name: str | None = None


class Tag(BaseModel):
    id: int | None = None
    name: str | None = None


class PetResponse(BaseModel):
    """Single Pet object as returned by the Petstore API.

    All fields are optional at the model level because the API is lenient and
    does not always echo back every field. The @field_validator on status logs
    a warning when the value is outside the documented enum but does not reject
    it, because the API itself accepts arbitrary strings.
    """

    id: int | None = None
    category: Category | None = None
    name: str | None = None
    photoUrls: list[str | None] = []
    tags: list[Tag] = []
    status: str | None = None

    @classmethod
    @field_validator("status", mode="before")
    def log_unexpected_status(cls, v: Any) -> Any:
        allowed = {s.value for s in PetStatus} | {None}
        if v not in allowed:
            logger.warning(
                f"Pet status '{v}' is outside the documented enum "
                f"({' | '.join(s.value for s in PetStatus)})"
            )
        return v


class ApiResponse(BaseModel):
    """Generic response envelope returned by upload and delete endpoints."""

    code: int | None = None
    type: str | None = None
    message: str | None = None
