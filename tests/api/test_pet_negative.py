import logging

import pytest

from models.enums import ContentType, HTTPStatus, PetEndpoint, PetStatus
from tests.api.assertions import validate_pet

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestPetNegative:
    """Negative and edge-case scenarios for Petstore /pet endpoints."""

    # ------------------------------------------------------------------
    # GET /pet/{petId}
    # ------------------------------------------------------------------

    def test_get_pet_nonexistent_id(self, api_session, api_url):
        """GET /pet/{petId} with an ID that does not exist -> 404."""
        response = api_session.get(f"{api_url}{PetEndpoint.PET.with_id(0)}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_get_pet_invalid_id_format(self, api_session, api_url):
        """GET /pet/{petId} with a non-integer string in the path -> 400 or 404.

        The spec expects an int64 petId; passing an arbitrary string tests
        that the server rejects or safely handles the malformed path segment.
        """
        response = api_session.get(f"{api_url}{PetEndpoint.PET.with_id('invalid_string')}")
        assert response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND)

    # ------------------------------------------------------------------
    # POST /pet — missing / invalid fields
    # ------------------------------------------------------------------

    def test_create_pet_missing_name(self, api_session, api_url):
        """POST /pet with missing 'name' field (required per spec).

        The Petstore API is lenient and may still return 200.
        We document the observed behavior rather than asserting a strict 400.
        """
        invalid_pet = {
            "id": 11111111,
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": PetStatus.AVAILABLE,
        }
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=invalid_pet)
        logger.info(f"Missing name response: {response.status_code}")
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.METHOD_NOT_ALLOWED
        )
        if response.status_code == HTTPStatus.OK:
            pet = validate_pet(response.json())
            api_session.delete(
                f"{api_url}{PetEndpoint.PET.with_id(pet.id or 11111111)}"
            )

    def test_create_pet_missing_photo_urls(self, api_session, api_url):
        """POST /pet with missing 'photoUrls' field (required per spec).

        photoUrls is the second required field alongside name. The API may
        accept the request leniently or reject it with 400/405.
        """
        invalid_pet = {
            "id": 11111112,
            "name": "NoPhotosPet",
            "status": PetStatus.AVAILABLE,
        }
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=invalid_pet)
        logger.info(f"Missing photoUrls response: {response.status_code}")
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.METHOD_NOT_ALLOWED
        )
        if response.status_code == HTTPStatus.OK:
            pet = validate_pet(response.json())
            api_session.delete(
                f"{api_url}{PetEndpoint.PET.with_id(pet.id or 11111112)}"
            )

    def test_create_pet_empty_body(self, api_session, api_url):
        """POST /pet with empty JSON body -> error or lenient 200."""
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json={})
        logger.info(f"Empty body response: {response.status_code}")
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.METHOD_NOT_ALLOWED
        )

    def test_create_pet_negative_id(self, api_session, api_url):
        """POST /pet with a negative ID value.

        The spec uses int64 for id but does not explicitly prohibit negatives.
        Documents whether the API accepts or rejects this boundary value.
        """
        pet = {
            "id": -1,
            "name": "NegativeIdPet",
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": PetStatus.AVAILABLE,
        }
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=pet)
        logger.info(f"Negative ID response: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.BAD_REQUEST)
        if response.status_code == HTTPStatus.OK:
            created = validate_pet(response.json())
            if created.id:
                api_session.delete(
                    f"{api_url}{PetEndpoint.PET.with_id(created.id)}"
                )

    def test_create_pet_invalid_status_enum(self, api_session, api_url):
        """POST /pet with a status value outside the allowed enum (available/pending/sold).

        The spec restricts status to three values. Documents whether the server
        enforces the enum or stores arbitrary strings.
        """
        pet = {
            "id": 11111113,
            "name": "BadStatusPet",
            "photoUrls": ["https://example.com/photo.jpg"],
            "status": "flying",
        }
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=pet)
        logger.info(
            f"Invalid enum status response: {response.status_code} — {response.text}"
        )
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.METHOD_NOT_ALLOWED
        )
        if response.status_code == HTTPStatus.OK:
            # Schema validator logs a warning for the non-enum status value
            created = validate_pet(response.json())
            api_session.delete(
                f"{api_url}{PetEndpoint.PET.with_id(created.id or 11111113)}"
            )

    # ------------------------------------------------------------------
    # PUT /pet — negative cases
    # ------------------------------------------------------------------

    def test_update_pet_nonexistent(self, api_session, api_url):
        """PUT /pet with an ID that was never created.

        The Petstore may silently create the pet or return 404. Either is
        documented behavior for this API.
        """
        ghost_pet = {
            "id": 0,
            "name": "GhostPet",
            "photoUrls": [],
            "status": PetStatus.AVAILABLE,
        }
        response = api_session.put(f"{api_url}{PetEndpoint.PET}", json=ghost_pet)
        logger.info(f"Update nonexistent: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND)

    def test_update_pet_missing_required_fields(self, api_session, api_url, created_pet):
        """PUT /pet with body that omits both required fields (name and photoUrls).

        Even on an existing pet, stripping required fields should ideally be
        rejected. Documents the server's actual enforcement behavior.
        """
        incomplete = {"id": created_pet["id"], "status": PetStatus.PENDING}
        response = api_session.put(f"{api_url}{PetEndpoint.PET}", json=incomplete)
        logger.info(
            f"PUT missing required fields: {response.status_code} — {response.text}"
        )
        assert response.status_code in (
            HTTPStatus.OK, HTTPStatus.BAD_REQUEST, HTTPStatus.METHOD_NOT_ALLOWED
        )

    # ------------------------------------------------------------------
    # DELETE /pet/{petId}
    # ------------------------------------------------------------------

    def test_delete_pet_nonexistent(self, api_session, api_url):
        """DELETE /pet/{petId} for a non-existent pet -> 404."""
        response = api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(0)}")
        assert response.status_code == HTTPStatus.NOT_FOUND

    def test_delete_pet_twice(self, api_session, api_url, sample_pet):
        """DELETE /pet/{petId} called twice on the same pet.

        The first delete should succeed (200). The second should return 404
        because the resource no longer exists (non-idempotent per spec behavior).
        """
        # Create a fresh pet to delete
        create_resp = api_session.post(
            f"{api_url}{PetEndpoint.PET}", json=sample_pet
        )
        assert create_resp.status_code == HTTPStatus.OK
        pet_id = create_resp.json()["id"]

        first = api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet_id)}")
        assert first.status_code == HTTPStatus.OK, (
            f"First delete failed: {first.status_code}"
        )

        second = api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet_id)}")
        assert second.status_code == HTTPStatus.NOT_FOUND, (
            f"Second delete on already-deleted pet expected "
            f"{HTTPStatus.NOT_FOUND}, got {second.status_code}"
        )

    def test_delete_pet_invalid_id_format(self, api_session, api_url):
        """DELETE /pet/{petId} with a non-integer string in the path -> 400 or 404.

        Passing a string where an int64 is expected tests malformed-path handling.
        """
        response = api_session.delete(
            f"{api_url}{PetEndpoint.PET.with_id('not_a_number')}"
        )
        logger.info(f"Delete invalid ID format: {response.status_code}")
        assert response.status_code in (HTTPStatus.BAD_REQUEST, HTTPStatus.NOT_FOUND)

    # ------------------------------------------------------------------
    # GET /pet/findByStatus
    # ------------------------------------------------------------------

    def test_find_by_status_invalid(self, api_session, api_url):
        """GET /pet/findByStatus with a value outside the allowed enum.

        Expects either an empty list (lenient) or 400 (strict validation).
        """
        response = api_session.get(
            f"{api_url}{PetEndpoint.FIND_BY_STATUS}",
            params={"status": "nonexistent_status"},
        )
        if response.status_code == HTTPStatus.OK:
            assert response.json() == []
        else:
            assert response.status_code == HTTPStatus.BAD_REQUEST

    def test_find_by_status_no_param(self, api_session, api_url):
        """GET /pet/findByStatus with no status query parameter at all."""
        response = api_session.get(f"{api_url}{PetEndpoint.FIND_BY_STATUS}")
        logger.info(f"No param response: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.BAD_REQUEST)

    # ------------------------------------------------------------------
    # POST /pet/{petId} — form-data update, negative
    # ------------------------------------------------------------------

    def test_form_update_nonexistent_pet(self, api_session, api_url):
        """POST /pet/{petId} form-data update for a pet that does not exist.

        Using a very large ID that is guaranteed not to exist. The spec does
        not define behavior clearly; documents what the server returns.
        """
        response = api_session.post(
            f"{api_url}{PetEndpoint.PET.with_id(999999999999)}",
            data={"name": "Ghost", "status": PetStatus.AVAILABLE},
            headers={"Content-Type": ContentType.FORM},
        )
        logger.info(f"Form update nonexistent pet: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND)

    # ------------------------------------------------------------------
    # GET /pet/findByTags — negative
    # ------------------------------------------------------------------

    def test_find_by_tags_no_param(self, api_session, api_url):
        """GET /pet/findByTags with no tags parameter -> 400 or empty list."""
        response = api_session.get(f"{api_url}{PetEndpoint.FIND_BY_TAGS}")
        logger.info(f"findByTags no param: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.BAD_REQUEST)

    def test_find_by_tags_nonexistent_tag(self, api_session, api_url):
        """GET /pet/findByTags with a tag value that no pet carries -> empty list."""
        response = api_session.get(
            f"{api_url}{PetEndpoint.FIND_BY_TAGS}",
            params={"tags": "this-tag-definitely-does-not-exist-xyz123"},
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert isinstance(body, list)
        assert body == [], f"Expected empty list for unknown tag, got: {body}"

    # ------------------------------------------------------------------
    # POST /pet/{petId}/uploadFile — negative
    # ------------------------------------------------------------------

    def test_upload_image_nonexistent_pet(self, upload_session, api_url, fake_image_file):
        """POST /pet/{petId}/uploadFile for a pet that does not exist.

        The server should reject the upload with 404 (pet not found).
        Documents actual behavior since the spec does not mandate a specific
        error code for this scenario.
        """
        response = upload_session.post(
            f"{api_url}{PetEndpoint.PET.upload_image(999999999999)}",
            files={"file": ("ghost.jpg", fake_image_file, ContentType.JPEG)},
        )
        logger.info(f"Upload to nonexistent pet: {response.status_code}")
        assert response.status_code in (HTTPStatus.OK, HTTPStatus.NOT_FOUND)
