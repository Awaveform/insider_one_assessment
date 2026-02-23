import logging
import time

from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class OpenPositionsPage(BasePage):
    """Page Object for the Insider Open Positions / Job Listings page."""

    # --- Filter dropdowns ---
    LOCATION_FILTER = (By.ID, "filter-by-location")
    DEPARTMENT_FILTER = (By.ID, "filter-by-department")

    # --- Job list ---
    JOB_LIST_CONTAINER = (By.ID, "jobs-list")
    JOB_ITEMS = (By.CSS_SELECTOR, ".position-list-item")

    # --- Per-item fields ---
    JOB_TITLE = (By.CSS_SELECTOR, ".position-list-item .position-title")
    JOB_DEPARTMENT = (By.CSS_SELECTOR, ".position-list-item .position-department")
    JOB_LOCATION = (By.CSS_SELECTOR, ".position-list-item .position-location")
    VIEW_ROLE_BUTTON = (By.CSS_SELECTOR, ".position-list-item a.btn")

    # --- Filter option constants ---
    QUALITY_ASSURANCE = "Quality Assurance"
    ISTANBUL_TURKIYE = "Istanbul, Turkiye"

    def filter_by_location(self, location: str) -> None:
        """Select a location from the location filter dropdown."""
        self.scroll_to_element(self.LOCATION_FILTER)
        self.set_dropdowns_option_by_option(
            locator=self.LOCATION_FILTER, option=location
        )
        logger.info(f"Jobs filtered by location '{location}'")

    def wait_until_positions_filtered_by_location(
            self,
            location: str
    ) -> bool:
        """Wait until all listed job locations match *location*.

        Returns:
            True when every job card shows the expected location.

        Raises:
            TimeoutError: When the condition is not met within the default timeout.
        """
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
        """Return the title text from every visible job card."""
        return [el.text for el in self.driver.find_elements(*self.JOB_TITLE)]

    def get_listed_positions_departments(self) -> list[str]:
        """Return the department text from every visible job card."""
        return [el.text for el in self.driver.find_elements(*self.JOB_DEPARTMENT)]

    def get_listed_positions_locations(self) -> list[str]:
        """Return the location text from every visible job card."""
        return [el.text for el in self.driver.find_elements(*self.JOB_LOCATION)]

    def filter_by_department(self, department: str) -> None:
        """Select a department from the department filter dropdown."""
        logger.info(f"Filtering by department: {department}")
        self.click(self.DEPARTMENT_FILTER)
        time.sleep(1)  # Wait for dropdown animation
        option = (By.XPATH, f"//li[contains(text(), '{department}')]")
        self.click(option)
        time.sleep(1)  # Wait for filter to apply

    def get_job_departments(self) -> list[str]:
        """Return the department text from all visible job listings."""
        elements = self.find_all(self.JOB_DEPARTMENT)
        return [el.text for el in elements]

    def get_job_locations(self) -> list[str]:
        """Return the location text from all visible job listings."""
        elements = self.find_all(self.JOB_LOCATION)
        return [el.text for el in elements]

    def click_view_role(self, index: int = 0) -> None:
        """Click the 'View Role' button on the *index*-th job card (0-indexed)."""
        logger.info(f"Clicking View Role on job index {index}")
        buttons = self.find_all(self.VIEW_ROLE_BUTTON)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            buttons[index],
        )
        time.sleep(0.5)  # Wait for hover animation to reveal the button
        buttons[index].click()

    def is_job_list_present(self) -> bool:
        """Return True if the job list container is visible and contains at least one item."""
        if not self.is_displayed(self.JOB_LIST_CONTAINER):
            return False
        items = self.driver.find_elements(*self.JOB_ITEMS)
        return len(items) > 0
