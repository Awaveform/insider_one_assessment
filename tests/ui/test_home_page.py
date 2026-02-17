import pytest

from pages.home_page import HomePage


@pytest.mark.ui
class TestHomePage:
    """Step 1: Verify insiderone.com homepage loads with all main blocks."""

    def test_homepage_is_opened(self, home_page: HomePage):
        """The homepage URL should contain insiderone.com."""
        current_url = home_page.get_current_url()
        assert "insiderone" in current_url.lower(), (
            f"Expected insiderone URL, got: {current_url}"
        )

    def test_navbar_is_visible(self, home_page: HomePage):
        """The navigation bar should be visible at the top of the page."""
        assert home_page.is_navbar_displayed(), "Navbar is not displayed"

    def test_hero_section_is_visible(self, home_page: HomePage):
        """The hero/banner section should be visible."""
        assert home_page.is_hero_section_displayed(), "Hero section is not displayed"

    def test_clients_section_is_visible(self, home_page: HomePage):
        """The clients/partners section should be visible."""
        assert home_page.is_clients_section_displayed(), (
            "Clients section is not displayed"
        )

    def test_footer_is_visible(self, home_page: HomePage):
        """The page footer should be visible."""
        assert home_page.is_footer_displayed(), "Footer is not displayed"
