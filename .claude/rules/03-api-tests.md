# API Test Rules

## Structure
- Base URL is defined in config/config.py as PETSTORE_BASE_URL.
- Tests use the requests library via the api_session fixture (tests/api/conftest.py).
- Group positive scenarios in test_pet_crud.py, negative in test_pet_negative.py.

## Test Patterns
- Each test should be independent. Use fixtures for setup/teardown.
- Always assert response status code first, then response body.
- For CRUD flows, the created_pet fixture handles creation + cleanup.
- Use @pytest.mark.parametrize for testing multiple values.
- Document known API quirks in test docstrings.

## Assertions
- Verify status codes match expected HTTP semantics (200 success, 404 not found).
- Verify response body structure: check key fields exist and have correct types.
- For negative tests where the API is lenient, log observed behavior and assert it.
- Never hard-code response body values that come from dynamic server state.

## Data Management
- Use large, unique IDs (e.g., 99887766) to avoid collisions.
- Always clean up created test data in fixture teardown.
