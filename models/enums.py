"""Project-wide enums — single source of truth for text/numeric constants.

Import from here instead of hard-coding strings or integers in tests,
fixtures, or page objects.  All enums inherit from the matching primitive
type so they compare equal to raw values and work in f-strings and dict
literals without any extra casting.

Usage examples::

    from models.enums import PetStatus, HTTPStatus, PetEndpoint

    assert response.status_code == HTTPStatus.OK
    params = {"status": PetStatus.AVAILABLE}          # works as "available"
    url = f"{base}{PetEndpoint.PET}"                  # works as "/pet"
"""

from enum import IntEnum, StrEnum


# ---------------------------------------------------------------------------
# Petstore domain
# ---------------------------------------------------------------------------

class PetStatus(StrEnum):
    """Valid values for the Petstore ``status`` field."""

    AVAILABLE = "available"
    PENDING = "pending"
    SOLD = "sold"


class PetEndpoint(StrEnum):
    """Petstore API path segments (appended to the base URL)."""

    PET = "/pet"
    FIND_BY_STATUS = "/pet/findByStatus"
    FIND_BY_TAGS = "/pet/findByTags"

    def with_id(self, pet_id: int | str) -> str:
        """Return ``/pet/{pet_id}`` — used for GET, DELETE, form-POST."""
        return f"/pet/{pet_id}"

    def upload_image(self, pet_id: int | str) -> str:
        """Return ``/pet/{pet_id}/uploadImage``."""
        return f"/pet/{pet_id}/uploadImage"


# ---------------------------------------------------------------------------
# HTTP protocol
# ---------------------------------------------------------------------------

class HTTPStatus(IntEnum):
    """HTTP response status codes used across the test suite."""

    OK = 200
    BAD_REQUEST = 400
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405


class ContentType(StrEnum):
    """MIME types used in ``Content-Type`` / ``Accept`` headers."""

    JSON = "application/json"
    FORM = "application/x-www-form-urlencoded"
    JPEG = "image/jpeg"


# ---------------------------------------------------------------------------
# Browser / UI
# ---------------------------------------------------------------------------

class Browser(StrEnum):
    """Browser identifiers accepted by the ``--browser`` CLI option."""

    CHROME = "chrome"
    FIREFOX = "firefox"
