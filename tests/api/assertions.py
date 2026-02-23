"""Response assertion helpers for Petstore API tests.

Wraps Pydantic models from models.petstore and calls pytest.fail() on
schema violations so failures appear as test errors with clear messages.
"""

from __future__ import annotations

import logging

import pytest
from pydantic import ValidationError

from models.petstore import ApiResponse, PetResponse

logger = logging.getLogger(__name__)


def validate_pet(body: dict) -> PetResponse:
    """Parse and validate a single pet response body.

    Calls pytest.fail() on schema violation so the failure is reported as a
    test error rather than an unhandled exception.
    """
    try:
        return PetResponse.model_validate(body)
    except ValidationError as exc:
        logger.error(f"Pet schema validation failed: {exc}")
        pytest.fail(f"Response body does not match PetResponse schema:\n{exc}")


def validate_api_response(body: dict) -> ApiResponse:
    """Parse and validate a generic ApiResponse envelope."""
    try:
        return ApiResponse.model_validate(body)
    except ValidationError as exc:
        logger.error(f"ApiResponse schema validation failed: {exc}")
        pytest.fail(f"Response body does not match ApiResponse schema:\n{exc}")


def validate_pet_list(body: list) -> list[PetResponse]:
    """Parse and validate every item in a pet list response.

    Collects all per-item errors before failing so a single call surfaces
    every broken item, not just the first.
    """
    errors: list[str] = []
    pets: list[PetResponse] = []
    for i, item in enumerate(body):
        try:
            pets.append(PetResponse.model_validate(item))
        except ValidationError as exc:
            errors.append(f"Item {i}: {exc}")

    if errors:
        logger.error(f"PetList schema validation failed: {errors}")
        pytest.fail(
            f"{len(errors)} pet(s) failed schema validation:\n"
            + "\n".join(errors)
        )
    return pets
