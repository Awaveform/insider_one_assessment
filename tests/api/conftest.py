import io
from typing import Any, AsyncGenerator, Generator

import httpx
import pytest
import pytest_asyncio
import requests
from requests import Session

from config.config import settings
from models.enums import ContentType, HTTPStatus, PetEndpoint, PetStatus


# ---------------------------------------------------------------------------
# Sync session fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="session")
def api_session() -> Generator[Session, Any, None]:
    """Provide a requests.Session pre-configured with JSON headers."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": ContentType.JSON,
        "Accept": ContentType.JSON,
    })
    yield session
    session.close()


@pytest.fixture(scope="session")
def upload_session() -> Generator[Session, Any, None]:
    """Provide a requests.Session without Content-Type for multipart uploads.

    The Content-Type (including boundary) is set automatically by requests
    when using the files= parameter. Setting it manually would break uploads.

    SSL verification is disabled because local AV/proxy software (e.g. Avast)
    intercepts TLS connections and re-signs them with a local CA that the
    requests certificate bundle does not trust.  This causes multipart bodies
    to be silently dropped, producing spurious 404s from the upload endpoint.
    """
    session = requests.Session()
    session.headers.update({"Accept": ContentType.JSON})
    session.verify = False
    yield session
    session.close()


# ---------------------------------------------------------------------------
# Async session fixtures
# ---------------------------------------------------------------------------

@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_api_client() -> AsyncGenerator[httpx.AsyncClient, Any]:
    """Provide an httpx.AsyncClient pre-configured with JSON headers."""
    async with httpx.AsyncClient(
        headers={
            "Content-Type": ContentType.JSON,
            "Accept": ContentType.JSON,
        },
        timeout=30.0,
    ) as client:
        yield client


@pytest_asyncio.fixture(scope="session", loop_scope="session")
async def async_upload_client() -> AsyncGenerator[httpx.AsyncClient, Any]:
    """Provide an httpx.AsyncClient without Content-Type for multipart uploads.

    The Content-Type (including boundary) is set automatically by httpx
    when using the files= parameter. Setting it manually would break uploads.

    SSL verification is disabled because local AV/proxy software (e.g. Avast)
    intercepts TLS connections and re-signs them with a local CA that the
    httpx certificate bundle does not trust. This causes multipart bodies
    to be silently dropped, producing spurious 404s from the upload endpoint.
    """
    async with httpx.AsyncClient(
        headers={"Accept": ContentType.JSON},
        verify=False,
        timeout=30.0,
    ) as client:
        yield client


# ---------------------------------------------------------------------------
# Sync URL / data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def api_url() -> str:
    """Return the Petstore API base URL."""
    return settings.petstore_base_url


@pytest.fixture
def sample_pet() -> dict:
    """Return a valid pet payload for test setup."""
    return {
        "id": 99887766,
        "category": {"id": 1, "name": "dog"},
        "name": "TestDoggo",
        "photoUrls": ["https://example.com/photo.jpg"],
        "tags": [{"id": 1, "name": "test-tag"}],
        "status": PetStatus.AVAILABLE,
    }


@pytest.fixture
def minimal_pet() -> dict:
    """Return a pet payload with required fields only (no id, category, tags, status)."""
    return {
        "name": "MinimalPet",
        "photoUrls": ["https://example.com/minimal.jpg"],
    }


@pytest.fixture
def created_pet(api_session, api_url, sample_pet) -> Generator[Any, Any, None]:
    """Create a pet via API and return the payload. Delete after test."""
    response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=sample_pet)
    assert response.status_code == HTTPStatus.OK, (
        f"Failed to create pet: {response.status_code} {response.text}"
    )
    pet_data = response.json()
    yield pet_data
    api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet_data['id'])}")


@pytest.fixture
def fake_image_file() -> io.BytesIO:
    """Return a minimal valid JPEG byte stream for upload tests."""
    return io.BytesIO(
        bytes.fromhex("ffd8ffe000104a46494600010100000001000100")
    )


# ---------------------------------------------------------------------------
# Async URL / data fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def async_api_url() -> str:
    """Return the Petstore API base URL."""
    return settings.petstore_base_url


@pytest.fixture
def async_sample_pet() -> dict:
    """Return a valid async pet payload for test setup."""
    return {
        "id": 99887755,
        "category": {"id": 1, "name": "dog"},
        "name": "AsyncTestDoggo",
        "photoUrls": ["https://example.com/photo.jpg"],
        "tags": [{"id": 1, "name": "async-test-tag"}],
        "status": PetStatus.AVAILABLE,
    }


@pytest.fixture
def async_minimal_pet() -> dict:
    """Return an async pet payload with required fields only (no id, category, tags, status)."""
    return {
        "name": "AsyncMinimalPet",
        "photoUrls": ["https://example.com/minimal.jpg"],
    }


@pytest_asyncio.fixture
async def async_created_pet(
    async_api_client: httpx.AsyncClient,
    async_api_url: str,
    async_sample_pet: dict,
) -> AsyncGenerator[dict, Any]:
    """Create a pet via API and return the payload. Delete after test."""
    response = await async_api_client.post(
        f"{async_api_url}{PetEndpoint.PET}", json=async_sample_pet
    )
    assert response.status_code == HTTPStatus.OK, (
        f"Failed to create pet: {response.status_code} {response.text}"
    )
    pet_data = response.json()
    yield pet_data
    await async_api_client.delete(
        f"{async_api_url}{PetEndpoint.PET.with_id(pet_data['id'])}"
    )


@pytest.fixture
def async_fake_image_file() -> io.BytesIO:
    """Return a minimal valid JPEG byte stream for async upload tests."""
    return io.BytesIO(
        bytes.fromhex("ffd8ffe000104a46494600010100000001000100")
    )
