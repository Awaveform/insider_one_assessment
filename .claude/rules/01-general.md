# General Project Rules

## Language and Framework
- All code is Python 3.11+.
- Use type hints on all function signatures.
- Use f-strings for string formatting.
- Import order: stdlib, third-party, local.

## Testing
- pytest is the only test runner. Do not use unittest.TestCase style.
- Every test function must have a docstring explaining what it verifies.
- Test names use the pattern: test_<what>_<expected_outcome>.
- Group related tests in classes prefixed with Test.
- Use pytest.mark decorators: @pytest.mark.ui, @pytest.mark.api, @pytest.mark.load.

## Error Handling
- Never silently catch and ignore exceptions in test utilities.
- Log all exceptions before re-raising.
- Use pytest.fail() with descriptive messages, not bare assert False.

## File Locations
- New page objects go in pages/ and must inherit BasePage.
- New UI tests go in tests/ui/.
- New API tests go in tests/api/.
- Configuration constants go in config/config.py, never hard-coded in tests.
