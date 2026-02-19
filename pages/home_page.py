import logging
from dataclasses import dataclass
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException


from config.config import Config
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlockCheckResult:
    missing: list[str]
    errors: list[str]

    def ok(self) -> bool:
        return not self.missing and not self.errors

    def to_message(self) -> str:
        parts: list[str] = []

        if self.missing:
            parts.append(
                "Missing/not visible blocks:\n"
                + "\n".join(f"- {name}" for name in self.missing)
            )

        if self.errors:
            parts.append(
                "Errors while checking blocks:\n"
                + "\n".join(f"- {line}" for line in self.errors)
            )

        return "\n\n".join(parts) if parts else "All blocks are visible."


class HomePage(BasePage):
    """Page Object for the Insider One homepage (insiderone.com)."""

    URL = Config.INSIDER_HOME_URL

    # Locators
    DEMO_BTN = (By.CSS_SELECTOR, "#navigation .btn.btn-primary")
    LOGIN_BTN = (
        By.XPATH,
        '//*[@class="header-top-action"]//*[normalize-space(.)="Login"]',
    )

    COOKIE_ACCEPT = (By.ID, "wt-cli-accept-all-btn")

    HEADER = (By.ID, "navigation")
    HERO = (By.CSS_SELECTOR, ".homepage-hero")
    SOCIAL_PROOF = (By.CSS_SELECTOR, ".homepage-social-proof")

    # NOTE: this looks suspicious in your code — it duplicates SOCIAL_PROOF.
    # If core differentiators has its own block, you likely want a different selector.
    CORE_DIFFERENTIATORS = (By.CSS_SELECTOR, ".homepage-social-proof")

    CAPABILITIES = (By.CSS_SELECTOR, ".homepage-capabilities")
    INSIDER_ONE_AI = (By.CSS_SELECTOR, ".homepage-insider-one-ai")
    CHANNELS = (By.CSS_SELECTOR, ".homepage-channels")
    CASE_STUDY = (By.CSS_SELECTOR, ".homepage-case-study")
    ANALYST = (By.CSS_SELECTOR, ".homepage-analyst")
    INTEGRATIONS = (By.CSS_SELECTOR, ".homepage-integrations")
    RESOURCES = (By.CSS_SELECTOR, ".homepage-resources")
    CALL_TO_ACTION = (By.CSS_SELECTOR, ".homepage-call-to-action")
    FOOTER = (By.ID, "footer")
    COOKIES_MODAL = (By.ID, "cookie-law-info-bar")

    def open_home(self) -> "HomePage":
        """Navigate to the Insider One homepage."""
        self.open(self.URL)
        return self

    def accept_cookies_if_present(self) -> None:
        """Dismiss the Cookie Consent Banner if it appears."""
        try:
            btn = WebDriverWait(self.driver, 5).until(
                EC.element_to_be_clickable(self.COOKIE_ACCEPT)
            )
            btn.click()
            logger.info("Cookie banner accepted")
        except TimeoutException:
            logger.info("Cookie banner not present")

    def _scroll_into_view_center(self, locator: tuple[str, str]) -> None:
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element,
        )

    def _is_block_visible(
            self, locator: tuple[str, str], *, scroll: bool = False
    ) -> bool:
        if scroll:
            self._scroll_into_view_center(locator)
        return self.is_displayed(locator)

    def check_main_blocks(self) -> BlockCheckResult:
        """
        Check that the main homepage blocks are visible.

        Returns a report (missing blocks + errors) so the test can assert.
        This keeps assertions out of the Page Object.
        """
        checks: list[tuple[str, Callable[[], bool]]] = [
            ("Header", lambda: self._is_block_visible(self.HEADER)),
            ("Hero section", lambda: self._is_block_visible(self.HERO)),
            ("Social proof section", lambda: self._is_block_visible(self.SOCIAL_PROOF)),
            ("Core differentiators section", lambda: self._is_block_visible(self.CORE_DIFFERENTIATORS)),
            ("Capabilities section", lambda: self._is_block_visible(self.CAPABILITIES)),
            ("Insider One AI section", lambda: self._is_block_visible(self.INSIDER_ONE_AI)),
            ("Channels section", lambda: self._is_block_visible(self.CHANNELS)),
            ("Case study section", lambda: self._is_block_visible(self.CASE_STUDY)),
            ("Analyst section", lambda: self._is_block_visible(self.ANALYST)),
            ("Integrations section", lambda: self._is_block_visible(self.INTEGRATIONS)),
            ("Resources section", lambda: self._is_block_visible(self.RESOURCES, scroll=True)),
            ("Call to action section", lambda: self._is_block_visible(self.CALL_TO_ACTION)),
            ("Footer", lambda: self._is_block_visible(self.FOOTER)),
            ("Cookies Modal", lambda: self._is_block_visible(self.COOKIES_MODAL)),
        ]

        missing: list[str] = []
        errors: list[str] = []

        for name, check in checks:
            try:
                if not check():
                    missing.append(name)
            except Exception as exc:  # noqa: BLE001
                errors.append(f"{name}: {type(exc).__name__}: {exc}")

        return BlockCheckResult(missing=missing, errors=errors)

    def get_current_url(self) -> str:
        return self.driver.current_url
