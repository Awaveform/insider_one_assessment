import logging

from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

logger = logging.getLogger(__name__)


class BasePage:
    """Base class for all Page Objects. Wraps Selenium calls with
    explicit waits and logging."""

    def __init__(self, driver: WebDriver, timeout: int = 15):
        self.driver = driver
        self.timeout = timeout
        self._wait = WebDriverWait(driver, timeout)

    def open(self, url: str) -> None:
        """Navigate to the given URL."""
        logger.info(f"Navigating to: {url}")
        self.driver.get(url)

    def find(self, locator: tuple) -> WebElement:
        """Wait for element to be present, then return it."""
        logger.debug(f"Finding element: {locator}")
        return self._wait.until(EC.presence_of_element_located(locator))

    def find_visible(self, locator: tuple) -> WebElement:
        """Wait for element to be visible, then return it."""
        return self._wait.until(EC.visibility_of_element_located(locator))

    def find_all(self, locator: tuple) -> list[WebElement]:
        """Wait for at least one element, then return all matches."""
        self._wait.until(EC.presence_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def find_all_visible(self, locator: tuple) -> list[WebElement]:
        """Wait for elements to be visible, then return all matches."""
        self._wait.until(EC.visibility_of_element_located(locator))
        return self.driver.find_elements(*locator)

    def click(self, locator: tuple) -> None:
        """Wait for element to be clickable, then click it."""
        logger.debug(f"Clicking element: {locator}")
        element = self._wait.until(EC.element_to_be_clickable(locator))
        element.click()

    def type_text(self, locator: tuple, text: str) -> None:
        """Clear field and type text into it."""
        element = self.find_visible(locator)
        element.clear()
        element.send_keys(text)

    def get_text(self, locator: tuple) -> str:
        """Return the visible text of an element."""
        return self.find_visible(locator).text

    def is_displayed(self, locator: tuple, timeout: int = 5) -> bool:
        """Check if element is visible within the given timeout."""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.visibility_of_element_located(locator)
            )
            return True
        except TimeoutException:
            return False

    def scroll_to_element(self, locator: tuple) -> WebElement:
        """Scroll an element into view and return it."""
        element = self.find(locator)
        self.driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'smooth', block: 'center'});",
            element,
        )
        return element

    def get_current_url(self) -> str:
        """Return the current page URL."""
        return self.driver.current_url

    def switch_to_new_tab(self) -> None:
        """Switch to the most recently opened tab."""
        windows = self.driver.window_handles
        self.driver.switch_to.window(windows[-1])

    def wait_for_url_contains(self, partial_url: str, timeout: int = 15) -> bool:
        """Wait until the current URL contains the given substring."""
        return WebDriverWait(self.driver, timeout).until(
            EC.url_contains(partial_url)
        )
