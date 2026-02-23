import logging

from selenium.webdriver.common.by import By

from config.config import settings
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CareersPage(BasePage):
    """Page Object for the Insider One Careers / Quality Assurance page."""

    URL = settings.insider_careers_qa_url

    # Locators
    PAGE_TITLE = (By.CSS_SELECTOR, "h1, .big-title")
    SEE_ALL_QA_JOBS = (By.XPATH, "//a[contains(text(), 'See all QA jobs')]")
    TEAMS_SECTION = (By.CSS_SELECTOR, ".job-team, [data-id='jobs'], .career-position-list")
    LOCATIONS_SECTION = (By.CSS_SELECTOR, ".location-slider, [class*='location']")
    LIFE_AT_INSIDER = (By.XPATH, "//*[contains(text(), 'Life at Insider')]")
    QA_DEPARTMENT = (By.XPATH, "//option[text()='Quality Assurance']")

    def open_qa_careers(self) -> "CareersPage":
        """Navigate to the QA Careers page."""
        self.open(self.URL)
        return self

    def click_see_all_qa_jobs(self) -> None:
        """Scroll to and click 'See all QA jobs', then wait for the Open Positions page to load."""
        self.scroll_to_element(self.SEE_ALL_QA_JOBS)
        self.click(self.SEE_ALL_QA_JOBS)
        self.find_visible_and_selected(self.QA_DEPARTMENT, timeout=60)
        logger.info("Clicked 'See all QA jobs'")

    def is_page_title_displayed(self) -> bool:
        """Check if the page title is visible."""
        return self.is_displayed(self.PAGE_TITLE)

    def is_teams_section_displayed(self) -> bool:
        """Check if the teams/jobs section is visible."""
        return self.is_displayed(self.TEAMS_SECTION)

    def is_locations_section_displayed(self) -> bool:
        """Check if the locations section is visible."""
        return self.is_displayed(self.LOCATIONS_SECTION)

    def is_life_at_insider_displayed(self) -> bool:
        """Check if the 'Life at Insider' section is visible."""
        return self.is_displayed(self.LIFE_AT_INSIDER)
