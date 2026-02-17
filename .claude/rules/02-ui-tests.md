# UI Test Rules

## Page Object Model
- Every web page under test has exactly one page object class.
- Page objects live in pages/ and inherit from BasePage.
- Locators are class-level constants using tuple format: (By.X, "value").
- Page object methods represent user-visible actions: click_login(), get_title().
- Page objects NEVER contain assertions. They return data for tests to assert.

## Selenium Best Practices
- ALWAYS use explicit waits (WebDriverWait + expected_conditions).
- NEVER use time.sleep() or implicit waits.
- NEVER call driver.find_element() directly in test files; use page object methods.
- Handle cookie consent banners in page object setup methods.
- When a click opens a new tab, use switch_to_new_tab() from BasePage.

## Browser Management
- The driver fixture handles browser lifecycle; tests never create drivers.
- Use --browser=chrome or --browser=firefox to select browser.
- Tests must work on both Chrome and Firefox without browser-specific code.
- Driver options (headless, window size) are configured in conftest.py only.

## Screenshots
- Screenshots on failure are automatic via pytest hook in tests/conftest.py.
- Do not add manual screenshot logic in individual tests.
- Screenshots are saved to screenshots/ with pattern FAIL_<test_id>_<timestamp>.png.
