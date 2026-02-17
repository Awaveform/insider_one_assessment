# CLAUDE.md - Project Guidance for Claude Code

## Project Overview
QA test automation assessment project with three parts:
1. **UI Tests** (Selenium) — Testing insiderone.com careers/QA workflows
2. **Load Tests** (Locust) — Performance testing n11.com search
3. **API Tests** (requests + pytest) — CRUD testing Petstore API

## Tech Stack
- Python 3.11+
- pytest (test runner for UI and API tests)
- Selenium WebDriver (UI automation)
- requests (API testing)
- Locust (load testing)
- webdriver-manager (automatic driver management)

## Project Structure
- `pages/` — Page Object Model classes (UI only). BasePage in base_page.py.
- `tests/ui/` — Selenium UI test files
- `tests/api/` — API test files using requests library
- `tests/load/` — Locust load test files (run separately, not via pytest)
- `config/` — Centralized configuration constants
- `utils/` — Logging and helper utilities
- `screenshots/` — Auto-populated on test failure
- `reports/` — Test reports output directory

## Key Commands
```bash
# Install dependencies
pip install -r requirements.txt

# Run all UI tests (Chrome)
pytest tests/ui/ --browser=chrome -v

# Run all UI tests (Firefox)
pytest tests/ui/ --browser=firefox -v

# Run API tests
pytest tests/api/ -v

# Run specific test file
pytest tests/ui/test_home_page.py -v

# Run load tests (headless, 1 user, 30s)
locust -f tests/load/locustfile.py --host=https://www.n11.com --users 1 --spawn-rate 1 --run-time 30s --headless

# Run load tests with web UI
locust -f tests/load/locustfile.py --host=https://www.n11.com
```

## Conventions
- All page objects inherit from `pages.base_page.BasePage`
- Locators are defined as class-level tuples: `(By.CSS_SELECTOR, ".class")`
- No assertions in page objects — tests handle all assertions
- No `time.sleep()` — use explicit waits via BasePage methods
- No BDD frameworks (no Behave, no Gherkin)
- Test files prefixed with `test_`, test classes prefixed with `Test`
- Fixtures go in conftest.py at the appropriate level
- The `driver` fixture provides single-browser selection via `--browser` flag
- Screenshot on failure is automatic via pytest hook in tests/conftest.py

## Important Notes
- insiderone.com may have cookie consent banners — always dismiss them first
- The Petstore API (petstore.swagger.io/v2) has known quirks: it may accept payloads missing required fields
- n11.com has bot detection — load tests use browser-like headers
- Lever application forms open in new tabs — tests must switch windows
