import logging

import pytest

from models.enums import ContentType, HTTPStatus, PetEndpoint, PetStatus
from tests.api.assertions import validate_api_response, validate_pet, validate_pet_list

logger = logging.getLogger(__name__)


@pytest.mark.api
class TestPetCRUD:
    """Positive CRUD scenarios for the Petstore /pet endpoints."""

    def test_create_pet_full_payload(self, api_session, api_url, sample_pet):
        """POST /pet — create a new pet with all fields populated.

        Verifies that id, name, status, category, tags, and photoUrls are
        all round-tripped correctly in the response body.
        """
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=sample_pet)
        assert response.status_code == HTTPStatus.OK, (
            f"Expected {HTTPStatus.OK}, got {response.status_code}"
        )
        body = response.json()
        pet = validate_pet(body)
        assert pet.id == sample_pet["id"]
        assert pet.name == sample_pet["name"]
        assert pet.status == sample_pet["status"]
        assert pet.category.name == sample_pet["category"]["name"]
        assert pet.photoUrls == sample_pet["photoUrls"]
        assert pet.tags[0].name == sample_pet["tags"][0]["name"]
        # Cleanup
        api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet.id)}")

    def test_create_pet_minimal_payload(
            self, api_session, api_url, minimal_pet
    ):
        """
        POST /pet — create a pet with required fields only (name + photoUrls).

        The spec marks only name and photoUrls as required; id, category,
        tags, and status are optional. Verifies the API accepts this minimal
        payload and returns the submitted values.
        """
        response = api_session.post(f"{api_url}{PetEndpoint.PET}", json=minimal_pet)
        assert response.status_code == HTTPStatus.OK, (
            f"Expected {HTTPStatus.OK}, got {response.status_code}: {response.text}"
        )
        body = response.json()
        pet = validate_pet(body)
        assert pet.name == minimal_pet["name"]
        assert pet.photoUrls == minimal_pet["photoUrls"]
        # Cleanup
        if pet.id:
            api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet.id)}")

    def test_get_pet_by_id(self, api_session, api_url, created_pet):
        """GET /pet/{petId} — retrieve a pet that exists."""
        pet_id = created_pet["id"]
        response = api_session.get(f"{api_url}{PetEndpoint.PET.with_id(pet_id)}")
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        pet = validate_pet(body)
        assert pet.id == pet_id
        assert pet.name == created_pet["name"]

    def test_update_pet_persists(self, api_session, api_url, created_pet):
        """
        PUT /pet — update name and status, then verify via GET that changes
        persisted.

        Asserting the PUT response body alone is insufficient because the
        server echoes the submitted data. A subsequent GET confirms the data
        was actually stored, not just echoed.
        """
        updated = {**created_pet, "name": "UpdatedDoggo", "status": PetStatus.SOLD}
        put_response = api_session.put(f"{api_url}{PetEndpoint.PET}", json=updated)
        assert put_response.status_code == HTTPStatus.OK
        put_pet = validate_pet(put_response.json())
        assert put_pet.name == "UpdatedDoggo"
        assert put_pet.status == PetStatus.SOLD

        # Persistence check: re-fetch and verify stored state
        get_response = api_session.get(
            f"{api_url}{PetEndpoint.PET.with_id(created_pet['id'])}"
        )
        assert get_response.status_code == HTTPStatus.OK, (
            f"GET after PUT returned {get_response.status_code}"
        )
        stored = validate_pet(get_response.json())
        assert stored.name == "UpdatedDoggo", (
            f"Name not persisted: got '{stored.name}'"
        )
        assert stored.status == PetStatus.SOLD, (
            f"Status not persisted: got '{stored.status}'"
        )

    def test_delete_pet(self, api_session, api_url, created_pet):
        """DELETE /pet/{petId} — remove a pet and verify it's gone."""
        pet_id = created_pet["id"]
        response = api_session.delete(f"{api_url}{PetEndpoint.PET.with_id(pet_id)}")
        assert response.status_code == HTTPStatus.OK
        # Verify deletion
        get_response = api_session.get(f"{api_url}{PetEndpoint.PET.with_id(pet_id)}")
        assert get_response.status_code == HTTPStatus.NOT_FOUND

    @pytest.mark.parametrize("status", list(PetStatus))
    def test_find_pet_by_status_single(self, api_session, api_url, status):
        """
        GET /pet/findByStatus — each valid status returns a list of
        matching pets.

        Verifies not only that the response is a list, but that every pet
        in the list actually carries the requested status value.
        """
        response = api_session.get(
            f"{api_url}{PetEndpoint.FIND_BY_STATUS}",
            params={"status": status},
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert isinstance(body, list), f"Expected list, got {type(body)}"
        pets = validate_pet_list(body)

        # Content validation: every returned pet must match the queried status
        mismatched = [p for p in pets if p.status != status]
        assert not mismatched, (
            f"Pets with wrong status returned for '{status}': "
            f"{[p.id for p in mismatched]}"
        )

    def test_find_pet_by_multiple_statuses(self, api_session, api_url):
        """
        GET /pet/findByStatus — querying two statuses returns pets from both.

        The status parameter is defined as an array in the spec, so multiple
        values can be passed in one request. Each returned pet's status must
        be one of the two requested values; the third (sold) must not appear
        (unless the test data happens to have none in that category).
        """
        queried = {PetStatus.AVAILABLE, PetStatus.PENDING}
        response = api_session.get(
            f"{api_url}{PetEndpoint.FIND_BY_STATUS}",
            params={"status": list(queried)},
        )
        assert response.status_code == HTTPStatus.OK
        body = response.json()
        assert isinstance(body, list)
        pets = validate_pet_list(body)

        invalid_statuses = [p for p in pets if p.status not in queried]
        assert not invalid_statuses, (
            f"Pets outside requested statuses returned: "
            f"{[(p.id, p.status) for p in invalid_statuses]}"
        )

    def test_update_pet_via_form_data(self, api_session, api_url, created_pet):
        """
        POST /pet/{petId} — update name and status via form-encoded data.

        This endpoint is distinct from PUT /pet:
        it uses application/x-www-form-urlencoded and accepts name +
        status as form fields, not a JSON body.
        """
        pet_id = created_pet["id"]
        response = api_session.post(
            f"{api_url}{PetEndpoint.PET.with_id(pet_id)}",
            data={"name": "FormUpdatedDoggo", "status": PetStatus.PENDING},
            headers={"Content-Type": ContentType.FORM},
        )
        assert response.status_code == HTTPStatus.OK, (
            f"Form update returned {response.status_code}: {response.text}"
        )

        # Verify the change persisted
        get_response = api_session.get(
            f"{api_url}{PetEndpoint.PET.with_id(pet_id)}"
        )
        assert get_response.status_code == HTTPStatus.OK
        stored = validate_pet(get_response.json())
        assert stored.name == "FormUpdatedDoggo", (
            f"Form name update not persisted: got '{stored.name}'"
        )
        assert stored.status == PetStatus.PENDING, (
            f"Form status update not persisted: got '{stored.status}'"
        )

    def test_find_pet_by_tags(self, api_session, api_url, created_pet):
        """
        GET /pet/findByTags — search returns pets that carry the queried tag.

        The endpoint is marked deprecated in the spec but remains functional.
        Uses the tag from the created_pet fixture ('test-tag') to guarantee
        at least one result.
        """
        tag_name = created_pet["tags"][0]["name"]
        response = api_session.get(
            f"{api_url}{PetEndpoint.FIND_BY_TAGS}",
            params={"tags": tag_name},
        )
        assert response.status_code == HTTPStatus.OK, (
            f"findByTags returned {response.status_code}"
        )
        body = response.json()
        assert isinstance(body, list)
        pets = validate_pet_list(body)
        # At least our created pet should appear
        ids_in_response = [p.id for p in pets]
        assert created_pet["id"] in ids_in_response, (
            f"Created pet {created_pet['id']} not found in findByTags results"
        )

    def test_upload_pet_image(
            self, upload_session, api_url, created_pet, fake_image_file
    ):
        """
        POST /pet/{petId}/uploadImage — upload a JPEG image for an existing pet.

        Uses multipart/form-data. The Content-Type header must NOT be pre-set;
        requests sets it automatically with the correct multipart boundary.
        Verifies the API acknowledges the upload with a 200 and a message body.
        """
        pet_id = created_pet["id"]
        response = upload_session.post(
            f"{api_url}{PetEndpoint.PET.upload_image(pet_id)}",
            files={"file": ("test_image.jpg", fake_image_file, ContentType.JPEG)},
        )
        assert response.status_code == HTTPStatus.OK, (
            f"Image upload returned {response.status_code}: {response.text}"
        )
        api_resp = validate_api_response(response.json())
        assert api_resp.message is not None, (
            f"Expected 'message' in upload response, got: {response.json()}"
        )

    def test_upload_pet_image_with_metadata(
            self, upload_session, api_url, created_pet, fake_image_file
    ):
        """
        POST /pet/{petId}/uploadImage — upload image with additionalMetadata
        field.

        The endpoint optionally accepts an additionalMetadata form string
        alongside the file. Verifies both fields are accepted and the response
        is 200.
        """
        pet_id = created_pet["id"]
        response = upload_session.post(
            f"{api_url}{PetEndpoint.PET.upload_image(pet_id)}",
            files={"file": ("photo.jpg", fake_image_file, ContentType.JPEG)},
            data={"additionalMetadata": "front-view"},
        )
        assert response.status_code == HTTPStatus.OK, (
            f"Upload with metadata returned {response.status_code}: "
            f"{response.text}"
        )
        api_resp = validate_api_response(response.json())
        assert api_resp.message is not None
