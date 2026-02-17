import logging
import time

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class OpenPositionsPage(BasePage):
    """Page Object for the Insider Open Positions / Job Listings page."""

    # Filter dropdowns
    LOCATION_FILTER = (By.ID, "select2-filter-by-location-container")
    DEPARTMENT_FILTER = (By.ID, "select2-filter-by-department-container")
    FILTER_DROPDOWN_SEARCH = (By.CSS_SELECTOR, "input.select2-search__field")
    FILTER_DROPDOWN_RESULTS = (By.CSS_SELECTOR, "ul.select2-results__options li")

    # Job list
    JOB_LIST_CONTAINER = (By.ID, "jobs-list")
    JOB_ITEMS = (By.CSS_SELECTOR, ".position-list-item")

    # Within each job item
    JOB_POSITION = (By.CSS_SELECTOR, ".position-list-item .position-title")
    JOB_DEPARTMENT = (By.CSS_SELECTOR, ".position-list-item .position-department")
    JOB_LOCATION = (By.CSS_SELECTOR, ".position-list-item .position-location")
    VIEW_ROLE_BUTTON = (By.CSS_SELECTOR, ".position-list-item a.btn")

    def filter_by_location(self, location: str) -> None:
        """Select a location from the location filter dropdown."""
        logger.info(f"Filtering by location: {location}")
        self.click(self.LOCATION_FILTER)
        time.sleep(1)  # Wait for dropdown animation
        option = (By.XPATH, f"//li[contains(text(), '{location}')]")
        self.click(option)
        time.sleep(1)  # Wait for filter to apply

    def filter_by_department(self, department: str) -> None:
        """Select a department from the department filter dropdown."""
        logger.info(f"Filtering by department: {department}")
        self.click(self.DEPARTMENT_FILTER)
        time.sleep(1)  # Wait for dropdown animation
        option = (By.XPATH, f"//li[contains(text(), '{department}')]")
        self.click(option)
        time.sleep(1)  # Wait for filter to apply

    def get_job_items(self) -> list:
        """Return all visible job listing elements."""
        return self.find_all(self.JOB_ITEMS)

    def get_job_positions(self) -> list[str]:
        """Return the Position text from all visible job listings."""
        elements = self.find_all(self.JOB_POSITION)
        return [el.text for el in elements]

    def get_job_departments(self) -> list[str]:
        """Return the Department text from all visible job listings."""
        elements = self.find_all(self.JOB_DEPARTMENT)
        return [el.text for el in elements]

    def get_job_locations(self) -> list[str]:
        """Return the Location text from all visible job listings."""
        elements = self.find_all(self.JOB_LOCATION)
        return [el.text for el in elements]

    def click_view_role(self, index: int = 0) -> None:
        """Click 'View Role' on the nth job listing (0-indexed)."""
        logger.info(f"Clicking View Role on job index {index}")
        buttons = self.find_all(self.VIEW_ROLE_BUTTON)
        # Scroll to the button to ensure it's visible and hover to reveal
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            buttons[index],
        )
        time.sleep(0.5)  # Wait for hover animation to reveal the button
        buttons[index].click()

    def is_job_list_present(self) -> bool:
        """Check if the job list container is visible and has items."""
        if not self.is_displayed(self.JOB_LIST_CONTAINER):
            return False
        items = self.driver.find_elements(*self.JOB_ITEMS)
        return len(items) > 0
