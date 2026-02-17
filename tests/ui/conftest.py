import pytest

from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.open_positions_page import OpenPositionsPage


@pytest.fixture
def home_page(driver) -> HomePage:
    """Provide a HomePage instance, navigated and with cookies accepted."""
    page = HomePage(driver)
    page.open_home()
    page.accept_cookies_if_present()
    return page


@pytest.fixture
def careers_page(driver) -> CareersPage:
    """Provide a CareersPage instance."""
    return CareersPage(driver)


@pytest.fixture
def open_positions_page(driver) -> OpenPositionsPage:
    """Provide an OpenPositionsPage instance."""
    return OpenPositionsPage(driver)
