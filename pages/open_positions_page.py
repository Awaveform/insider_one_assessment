import logging
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class OpenPositionsPage(BasePage):
    """Page Object for the Insider Open Positions / Job Listings page."""

    # Filter dropdowns
    LOCATION_FILTER = (By.ID, "filter-by-location")
    DEPARTMENT_FILTER = (By.ID, "filter-by-department")
    FILTER_DROPDOWN_SEARCH = (By.CSS_SELECTOR, "input.select2-search__field")
    FILTER_DROPDOWN_RESULTS = (
        By.CSS_SELECTOR, "ul.select2-results__options li"
    )

    # Job list
    JOB_LIST_CONTAINER = (By.ID, "jobs-list")
    JOB_ITEMS = (By.CSS_SELECTOR, ".position-list-item")

    # Within each job item
    JOB_TITLE = (By.CSS_SELECTOR, ".position-list-item .position-title")
    JOB_DEPARTMENT = (
        By.CSS_SELECTOR, ".position-list-item .position-department"
    )
    JOB_LOCATION = (
        By.CSS_SELECTOR, ".position-list-item .position-location"
    )
    VIEW_ROLE_BUTTON = (By.CSS_SELECTOR, ".position-list-item a.btn")

    # Dropdown Departments
    QUALITY_ASSURANCE = "Quality Assurance"

    # Dropdown Locations
    ISTANBUL_TURKIYE = "Istanbul, Turkiye"

    def filter_by_location(self, location: str) -> None:
        """Select a location from the location filter dropdown."""
        self.set_dropdowns_option_by_option(
            locator=self.LOCATION_FILTER, option=location
        )
        logger.info(f"Jobs were filtered by location '{location}'")

    def wait_until_positions_filtered_by_location(
            self,
            location: str
    ) -> bool:
        try:
            self._wait.until(
                lambda d: (
                        (els := d.find_elements(*self.JOB_LOCATION))
                        and
                        all(location in el.text for el in els)
                )
            )
            return True
        except TimeoutException:
            raise TimeoutError(
                f"No job list filtered by location='{location}' "
                f"within {self.timeout}s"
            )

    def get_listed_positions_titles(self) -> list[str]:
        return [
            el.text
            for el in self.driver.find_elements(*self.JOB_TITLE)
        ]

    def get_listed_positions_departments(self) -> list[str]:
        return [
            el.text
            for el in self.driver.find_elements(*self.JOB_DEPARTMENT)
        ]

    def get_listed_positions_locations(self) -> list[str]:
        return [
            el.text
            for el in self.driver.find_elements(*self.JOB_LOCATION)
        ]


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
