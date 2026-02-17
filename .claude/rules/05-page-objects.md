# Page Object Model Conventions

## Naming
- File: snake_case matching the page (home_page.py, careers_page.py).
- Class: PascalCase matching the page (HomePage, CareersPage).
- Locator constants: UPPER_SNAKE_CASE (NAV_BAR, HERO_SECTION, JOB_ITEMS).
- Methods: snake_case verb phrases (click_see_all_jobs, get_job_titles).

## Structure Template
Every page object file follows this structure:
1. Imports (By, BasePage)
2. Class definition with URL constant
3. Locator constants grouped by page section
4. Constructor (only if adding page-specific init beyond BasePage)
5. Action methods (click, type, select)
6. Query methods (is_displayed, get_text, get_list)

## Locator Strategy Priority
1. By.ID — most stable, prefer when available
2. By.CSS_SELECTOR — for class-based or structural selectors
3. By.XPATH — only when CSS cannot express the query (text-based lookups)
4. By.LINK_TEXT — only for visible stable anchor text
Avoid By.CLASS_NAME and By.TAG_NAME (too brittle).

## Return Types
- Action methods return None or self (for chaining).
- Query methods return str, bool, list[str], or list[WebElement].
- Navigation methods may return the target page object instance.
