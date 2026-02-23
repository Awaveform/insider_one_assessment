import logging
from dataclasses import dataclass
from typing import Callable

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

from config.config import settings
from pages.base_page import BasePage

logger = logging.getLogger(__name__)


@dataclass(frozen=True)
class BlockCheckResult:
    """Result of a homepage block visibility check.

    Attributes:
        missing: Names of blocks that were not visible.
        errors:  Error messages for blocks that raised exceptions.
    """

    missing: list[str]
    errors: list[str]

    def ok(self) -> bool:
        """Return True when no blocks are missing and no errors occurred."""
        return not self.missing and not self.errors

    def to_message(self) -> str:
        """Return a human-readable summary of the check result."""
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

    URL = settings.insider_home_url

    # --- Navigation ---
    COOKIE_ACCEPT = (By.ID, "wt-cli-accept-all-btn")

    # --- Page sections ---
    HEADER = (By.ID, "navigation")
    HERO = (By.CSS_SELECTOR, ".homepage-hero")
    SOCIAL_PROOF = (By.CSS_SELECTOR, ".homepage-social-proof")
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

    def accept_cookies(self) -> None:
        """Wait for the cookie consent banner and click accept."""
        logger.info("Waiting for cookie banner and accepting")
        self.click(self.COOKIE_ACCEPT)

    def _scroll_into_view_center(self, locator: tuple[str, str]) -> None:
        """Scroll the element identified by *locator* to the centre of the viewport."""
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            element,
        )

    def _is_block_visible(
            self, locator: tuple[str, str], *, scroll: bool = False
    ) -> bool:
        """Return True if the block is currently visible.

        Args:
            locator: Selenium locator tuple for the block element.
            scroll:  When True, scroll the element into view and wait for
                     visibility before checking.
        """
        if scroll:
            self._scroll_into_view_center(locator)
            return bool(self.find_visible(locator))
        return self.is_displayed(locator)

    def is_cookies_modal_displayed(self) -> bool:
        """Return True if the cookie consent banner is currently visible."""
        return self.is_displayed(self.COOKIES_MODAL)

    def check_main_blocks(self) -> BlockCheckResult:
        """Verify that all main homepage sections are visible.

        Checks each named section in sequence, collecting any that are
        missing or raise an unexpected exception.  Assertions are left to
        the calling test so this method remains assertion-free.

        Returns:
            BlockCheckResult: A frozen dataclass with ``missing`` and
            ``errors`` lists; call ``.ok()`` to get a single bool.
        """
        checks: list[tuple[str, Callable[[], bool]]] = [
            ("Header", lambda: self._is_block_visible(self.HEADER)),
            ("Hero section", lambda: self._is_block_visible(self.HERO)),
            ("Social proof section", lambda: self._is_block_visible(self.SOCIAL_PROOF)),
            ("Capabilities section", lambda: self._is_block_visible(self.CAPABILITIES)),
            ("Insider One AI section", lambda: self._is_block_visible(self.INSIDER_ONE_AI)),
            ("Channels section", lambda: self._is_block_visible(self.CHANNELS)),
            ("Case study section", lambda: self._is_block_visible(self.CASE_STUDY)),
            ("Analyst section", lambda: self._is_block_visible(self.ANALYST)),
            ("Integrations section", lambda: self._is_block_visible(self.INTEGRATIONS)),
            ("Resources section", lambda: self._is_block_visible(self.RESOURCES, scroll=True)),
            ("Call to action section", lambda: self._is_block_visible(self.CALL_TO_ACTION)),
            ("Footer", lambda: self._is_block_visible(self.FOOTER)),
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
