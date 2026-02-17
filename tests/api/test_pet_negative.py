import logging

import pytest

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestPetNegative:
    """Negative and edge-case scenarios for Petstore /pet endpoints."""

    def test_get_pet_nonexistent_id(self, api_session, api_url):
        """GET /pet/{petId} with an ID that does not exist -> 404."""
        response = api_session.get(f"{api_url}/pet/0")
        assert response.status_code == 404

    def test_get_pet_invalid_id_format(self, api_session, api_url):
        """GET /pet/{petId} with a string instead of integer -> 404."""
        response = api_session.get(f"{api_url}/pet/invalid_string")
        assert response.status_code in (400, 404)

    def test_delete_pet_nonexistent(self, api_session, api_url):
        """DELETE /pet/{petId} for a non-existent pet -> 404."""
        response = api_session.delete(f"{api_url}/pet/0")
        assert response.status_code == 404

    def test_create_pet_missing_required_field(self, api_session, api_url):
        """POST /pet with missing 'name' field (required per spec).

        Note: The Petstore API is lenient and may still return 200.
        We document the observed behavior.
        """
        invalid_pet = {
            "id": 11111111,
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": "available",
        }
        response = api_session.post(f"{api_url}/pet", json=invalid_pet)
        logger.info(f"Missing name response: {response.status_code}")
        # Petstore accepts this — document the behavior
        assert response.status_code in (200, 400, 405)
        # Cleanup if created
        if response.status_code == 200:
            api_session.delete(f"{api_url}/pet/11111111")

    def test_create_pet_empty_body(self, api_session, api_url):
        """POST /pet with empty JSON body -> error or lenient 200."""
        response = api_session.post(f"{api_url}/pet", json={})
        logger.info(f"Empty body response: {response.status_code}")
        assert response.status_code in (200, 400, 405)

    def test_find_by_status_invalid(self, api_session, api_url):
        """GET /pet/findByStatus with invalid status value."""
        response = api_session.get(
            f"{api_url}/pet/findByStatus",
            params={"status": "nonexistent_status"},
        )
        if response.status_code == 200:
            assert response.json() == []
        else:
            assert response.status_code == 400

    def test_find_by_status_no_param(self, api_session, api_url):
        """GET /pet/findByStatus with no status param."""
        response = api_session.get(f"{api_url}/pet/findByStatus")
        logger.info(f"No param response: {response.status_code}")
        assert response.status_code in (200, 400)

    def test_update_pet_nonexistent(self, api_session, api_url):
        """PUT /pet with an ID that was never created."""
        ghost_pet = {
            "id": 0,
            "name": "GhostPet",
            "photoUrls": [],
            "status": "available",
        }
        response = api_session.put(f"{api_url}/pet", json=ghost_pet)
        logger.info(f"Update nonexistent: {response.status_code}")
        # Petstore may create or return error — document behavior
        assert response.status_code in (200, 404)

    def test_create_pet_negative_id(self, api_session, api_url):
        """POST /pet with a negative ID value."""
        pet = {
            "id": -1,
            "name": "NegativeIdPet",
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": "available",
        }
        response = api_session.post(f"{api_url}/pet", json=pet)
        logger.info(f"Negative ID response: {response.status_code}")
        assert response.status_code in (200, 400)
        # Cleanup if created
        if response.status_code == 200:
            pet_id = response.json().get("id")
            if pet_id:
                api_session.delete(f"{api_url}/pet/{pet_id}")
