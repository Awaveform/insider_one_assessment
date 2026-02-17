import pytest
import requests

from config.config import Config


@pytest.fixture(scope="session")
def api_session() -> requests.Session:
    """Provide a requests.Session pre-configured with JSON headers."""
    session = requests.Session()
    session.headers.update({
        "Content-Type": "application/json",
        "Accept": "application/json",
    })
    yield session
    session.close()


@pytest.fixture
def api_url() -> str:
    """Return the Petstore API base URL."""
    return Config.PETSTORE_BASE_URL


@pytest.fixture
def sample_pet() -> dict:
    """Return a valid pet payload for test setup."""
    return {
        "id": 99887766,
        "category": {"id": 1, "name": "dog"},
        "name": "TestDoggo",
        "photoUrls": ["https://example.com/photo.jpg"],
        "tags": [{"id": 1, "name": "test-tag"}],
        "status": "available",
    }


@pytest.fixture
def created_pet(api_session, api_url, sample_pet) -> dict:
    """Create a pet via API and return the payload. Delete after test."""
    response = api_session.post(f"{api_url}/pet", json=sample_pet)
    assert response.status_code == 200, (
        f"Failed to create pet: {response.status_code} {response.text}"
    )
    pet_data = response.json()
    yield pet_data
    # Teardown: delete the pet
    api_session.delete(f"{api_url}/pet/{pet_data['id']}")
