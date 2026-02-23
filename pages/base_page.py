import logging

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import TimeoutException, \
    StaleElementReferenceException

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all Page Objects. Wraps Selenium calls with
    explicit waits and logging."""

    def __init__(self, driver: WebDriver, timeout: int = 30):
        self.driver = driver
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        """Navigate to the given URL."""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def find(self, locator: WebElement | tuple[str, str]) -> WebElement:
        """Wait for element presence, then return it."""
        logger.debug(f"Finding element: {locator}")
        return self._wait.until(EC.presence_of_element_located(locator))

    def find_visible(
            self, locator: WebElement | tuple[str, str]
    ) -> WebElement:
        """Wait for element visibility, then return it."""
        logger.debug(f"Finding visible element: {locator}")
        return self._wait.until(EC.visibility_of_element_located(locator))

    def find_all(
            self, locator: WebElement | tuple[str, str]
    ) -> list[WebElement]:
        """Wait for at least one element to be present, then return all matches."""
        logger.debug(f"Finding all elements: {locator}")
        self._wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def find_all_visible(
            self, locator: WebElement | tuple[str, str]
    ) -> list[WebElement]:
        """Wait for at least one element to be visible, then return all matches."""
        logger.debug(f"Finding all visible elements: {locator}")
        self._wait.until(EC.visibility_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def find_visible_and_selected(
            self,
            locator: tuple[str, str],
            timeout: int | float | None = None
    ) -> WebElement:
        """Wait until the element is both visible and selected, then return it."""
        logger.debug(f"Waiting for visible+selected element: {locator}")
        wait = WebDriverWait(
            self.driver,
            timeout or self._wait._timeout
        )

        def _condition(driver):
            try:
                element = driver.find_element(*locator)
                return element if (
                        element.is_displayed()
                        and element.is_selected()
                ) else False
            except StaleElementReferenceException:
                return False

        return wait.until(_condition)

    def set_dropdowns_option_by_option(
            self,
            locator: tuple[str, str],
            option: str
    ) -> None:
        """Select *option* from a native ``<select>`` element by visible text.

        After selecting, waits until the dropdown's first selected option
        matches *option*.

        Raises:
            TimeoutError: When the selection does not take effect within the
                default timeout.
        """
        logger.info(f"Selecting dropdown option '{option}' for locator {locator}")
        dropdown = self._wait.until(
            EC.presence_of_element_located(locator)
        )

        Select(dropdown).select_by_visible_text(option)

        try:
            self._wait.until(
                lambda d: Select(
                    d.find_element(*locator)
                ).first_selected_option.text.strip() == option
            )
            logger.debug(f"Dropdown confirmed option '{option}'")
        except TimeoutException:
            raise TimeoutError(
                f"Dropdown did not switch to '{option}' within {self.timeout}s "
                f"for locator={locator}"
            )

    def click(self, locator: WebElement | tuple[str, str]) -> None:
        """Wait for element to be clickable, then click it."""
        logger.debug(f"Clicking element: {locator}")
        element = self._wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(
            self, locator: WebElement | tuple[str, str], text: str
    ) -> None:
        """Clear the field identified by *locator* and type *text* into it."""
        logger.debug(f"Typing into {locator}: '{text}'")
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: WebElement | tuple[str, str]) -> str:
        """Return the visible text of the element identified by *locator*."""
        logger.debug(f"Getting text of element: {locator}")
        return self.find_visible(locator).text

    def is_displayed(
            self, locator: WebElement | tuple[str, str], timeout: int = 5
    ) -> bool:
        """Return True if the element is visible within *timeout* seconds."""
        logger.debug(f"Checking visibility of element: {locator}")
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to_element(
            self, locator: WebElement | tuple[str, str]
    ) -> WebElement:
        """Scroll the element into view and return it."""
        logger.debug(f"Scrolling to element: {locator}")
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )
        return element

    def get_current_url(self) -> str:
        """Return the current page URL."""
        url = self.driver.current_url
        logger.debug(f"Current URL: {url}")
        return url

    def switch_to_new_tab(self) -> None:
        """Switch focus to the most recently opened browser tab."""
        logger.info("Switching to new tab")
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])
        logger.debug(f"Switched to window: {self.driver.current_url}")

    def wait_for_url_contains(
            self, partial_url: str, timeout: int = 15
    ) -> bool:
        """Wait until the current URL contains *partial_url*.

        Returns:
            True when the condition is satisfied within *timeout* seconds.
        """
        logger.info(f"Waiting for URL to contain: '{partial_url}'")
        return WebDriverWait(self.driver, timeout).until(
            EC.url_contains(partial_url)
        )
