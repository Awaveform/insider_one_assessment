import os
import logging

import pytest
from datetime import datetime
from selenium import webdriver

from pages.careers_page import CareersPage
from pages.home_page import HomePage
from pages.open_positions_page import OpenPositionsPage

logger = logging.getLogger(__name__)

SCREENSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(__file__)), "screenshots"
)


def pytest_addoption(parser):
    """Add custom CLI options for browser selection."""
    parser.addoption(
        "--browser",
        action="store",
        default="chrome",
        choices=["chrome", "firefox"],
        help="Browser to run UI tests: chrome or firefox",
    )


@pytest.fixture(scope="class")
def driver(request):
    """Single-browser fixture controlled by --browser CLI flag."""
    browser_name = request.config.getoption(name="--browser", default="chrome")
    yield from _create_driver(browser_name)


def _create_driver(browser_name: str):
    """Factory function to instantiate the requested browser driver."""
    logger.info(f"Setting up {browser_name} driver")

    if browser_name == "chrome":
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument("--disable-notifications")
        options.add_argument("--disable-popup-blocking")
        _driver = webdriver.Chrome(options=options)
    elif browser_name == "firefox":
        options = webdriver.FirefoxOptions()
        options.add_argument("--width=1920")
        options.add_argument("--height=1080")
        _driver = webdriver.Firefox(options=options)
    else:
        raise ValueError(f"Unsupported browser: {browser_name}")

    _driver.implicitly_wait(0)  # We use explicit waits only
    yield _driver

    logger.info(f"Tearing down {browser_name} driver")
    _driver.quit()


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Pytest hook: capture screenshot on test failure."""
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        _driver = item.funcargs.get("driver")
        if _driver:
            _take_screenshot(_driver, item.nodeid)


def _take_screenshot(driver, nodeid: str) -> None:
    """Save a screenshot with a descriptive filename based on the test ID."""
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
    """Return HomePage instance."""
    return HomePage(driver)


@pytest.fixture
def careers(driver) -> CareersPage:
    """Return CareersPage instance."""
    return CareersPage(driver)


@pytest.fixture
def positions(driver) -> OpenPositionsPage:
    """Return OpenPositionsPage instance."""
    return OpenPositionsPage(driver)
