import os
import logging

import pytest
from datetime import datetime
from selenium import webdriver

from models.enums import Browser
from pages.careers_page import CareersPage
from pages.home_page import HomePage
from pages.open_positions_page import OpenPositionsPage

logger = logging.getLogger(__name__)

PROJECT_ROOT = os.path.dirname(os.path.dirname(__file__))
SCREENSHOT_DIR = os.path.join(PROJECT_ROOT, "screenshots")


def pytest_configure(config):
    """Create the screenshots output directory before any test runs."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)


def pytest_addoption(parser):
    """Add custom CLI options for browser selection."""
    parser.addoption(
        "--browser",
        action="store",
        default=Browser.CHROME,
        choices=[b.value for b in Browser],
        help="Browser to run UI tests: chrome or firefox",
    )


@pytest.fixture(scope="class")
def driver(request):
    """Single-browser fixture controlled by --browser CLI flag."""
    browser_name = request.config.getoption(name="--browser", default=Browser.CHROME)
    yield from _create_driver(browser_name)


def _create_driver(browser_name: str):
    """Instantiate and yield the requested browser driver, then quit it.

    When the HEADLESS environment variable is set to '1' (e.g. inside Docker),
    Chrome/Firefox are started in headless mode automatically.
    """
    logger.info(f"Setting up {browser_name} driver")
    headless = os.environ.get("HEADLESS", "0") == "1"

    if browser_name == Browser.CHROME:
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        if headless:
            options.add_argument("--headless=new")
            options.add_argument("--no-sandbox")
            options.add_argument("--disable-dev-shm-usage")
            options.add_argument("--disable-gpu")
            options.add_argument("--window-size=1920,1080")
        _driver = webdriver.Chrome(options=options)
    elif browser_name == Browser.FIREFOX:
        options = webdriver.FirefoxOptions()
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        if headless:
            options.add_argument("--headless")
        _driver = webdriver.Firefox(options=options)
        _driver.maximize_window()
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    _driver.implicitly_wait(0)  # We use explicit waits only
    yield _driver

    logger.info(f"Tearing down {browser_name} driver")
    _driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook: capture a screenshot when a test fails."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        _driver = item.funcargs.get("driver")
        if _driver:
            _take_screenshot(_driver, item.nodeid)


def _take_screenshot(driver, nodeid: str) -> None:
    """Save a failure screenshot to the screenshots/ directory."""
    os.makedirs(SCREENSHOT_DIR, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    test_name = nodeid.replace("::", "_").replace("/", "_").replace("\\", "_")
    filename = f"FAIL_{test_name}_{timestamp}.png"
    filepath = os.path.join(SCREENSHOT_DIR, filename)

    try:
        driver.save_screenshot(filepath)
        logger.error(f"Screenshot saved: {filepath}")
    except Exception as e:
        logger.error(f"Failed to save screenshot: {e}")


@pytest.fixture
def home(driver) -> HomePage:
    """Return an InsiderOneHomePage instance backed by the active driver."""
    return HomePage(driver)


@pytest.fixture
def careers(driver) -> CareersPage:
    """Return a CareersPage instance backed by the active driver."""
    return CareersPage(driver)


@pytest.fixture
def positions(driver) -> OpenPositionsPage:
    """Return an OpenPositionsPage instance backed by the active driver."""
    return OpenPositionsPage(driver)
