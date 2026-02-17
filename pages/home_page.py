import logging

from selenium.webdriver.common.by import By

from config.config import Config
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class HomePage(BasePage):
    """Page Object for the Insider One homepage (insiderone.com)."""

    URL = Config.INSIDER_HOME_URL

    # Locators
    NAV_BAR = (By.CSS_SELECTOR, "nav.navbar")
    HERO_SECTION = (By.CSS_SELECTOR, "#hero-section, .hero-section, [data-bg-animation]")
    CLIENTS_SECTION = (By.XPATH, "//*[contains(@class, 'elementor')]//img[@alt]/..")
    FOOTER = (By.CSS_SELECTOR, "footer")
    COOKIE_ACCEPT = (By.ID, "wt-cli-accept-all-btn")

    def open_home(self) -> "HomePage":
        """Navigate to the Insider One homepage."""
        self.open(self.URL)
        return self

    def accept_cookies_if_present(self) -> None:
        """Dismiss the cookie consent banner if it appears."""
        if self.is_displayed(self.COOKIE_ACCEPT, timeout=5):
            self.click(self.COOKIE_ACCEPT)
            logger.info("Cookie consent accepted")

    def is_navbar_displayed(self) -> bool:
        """Check if the navigation bar is visible."""
        return self.is_displayed(self.NAV_BAR)

    def is_hero_section_displayed(self) -> bool:
        """Check if the hero/banner section is visible."""
        return self.is_displayed(self.HERO_SECTION)

    def is_clients_section_displayed(self) -> bool:
        """Check if the clients/partners section is visible."""
        return self.is_displayed(self.CLIENTS_SECTION)

    def is_footer_displayed(self) -> bool:
        """Check if the page footer is visible."""
        return self.is_displayed(self.FOOTER)
