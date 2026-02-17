import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestPetCRUD:
    """Positive CRUD scenarios for the Petstore /pet endpoints."""

    def test_create_pet(self, api_session, api_url, sample_pet):
        """POST /pet — create a new pet with valid payload."""
        response = api_session.post(f"{api_url}/pet", json=sample_pet)
        assert response.status_code == 200, (
            f"Expected 200, got {response.status_code}"
        )
        body = response.json()
        assert body["id"] == sample_pet["id"]
        assert body["name"] == sample_pet["name"]
        assert body["status"] == sample_pet["status"]
        # Cleanup
        api_session.delete(f"{api_url}/pet/{body['id']}")

    def test_get_pet_by_id(self, api_session, api_url, created_pet):
        """GET /pet/{petId} — retrieve a pet that exists."""
        pet_id = created_pet["id"]
        response = api_session.get(f"{api_url}/pet/{pet_id}")
        assert response.status_code == 200
        body = response.json()
        assert body["id"] == pet_id
        assert body["name"] == created_pet["name"]

    def test_update_pet(self, api_session, api_url, created_pet):
        """PUT /pet — update an existing pet's name and status."""
        updated = {**created_pet, "name": "UpdatedDoggo", "status": "sold"}
        response = api_session.put(f"{api_url}/pet", json=updated)
        assert response.status_code == 200
        body = response.json()
        assert body["name"] == "UpdatedDoggo"
        assert body["status"] == "sold"

    def test_delete_pet(self, api_session, api_url, created_pet):
        """DELETE /pet/{petId} — remove a pet and verify it's gone."""
        pet_id = created_pet["id"]
        response = api_session.delete(f"{api_url}/pet/{pet_id}")
        assert response.status_code == 200
        # Verify deletion
        get_response = api_session.get(f"{api_url}/pet/{pet_id}")
        assert get_response.status_code == 404

    @pytest.mark.parametrize("status", ["available", "pending", "sold"])
    def test_find_pet_by_status(self, api_session, api_url, status):
        """GET /pet/findByStatus — search with each valid status value."""
        response = api_session.get(
            f"{api_url}/pet/findByStatus",
            params={"status": status},
        )
        assert response.status_code == 200
        body = response.json()
        assert isinstance(body, list), f"Expected list, got {type(body)}"
