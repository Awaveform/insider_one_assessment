import pytest

from config.config import Config


@pytest.mark.ui
class TestJobApplication:
    """Step 4: Click 'View Role' and verify redirect to Lever application form."""

    def test_view_role_redirects_to_lever(self, home, careers, positions):
        """Click View Role on the first job and verify Lever application URL."""
        home.open_home()
        home.accept_cookies_if_present()

        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()

        positions.filter_by_location("Istanbul, Turkey")
        positions.filter_by_department("Quality Assurance")

        assert positions.is_job_list_present(), "No job listings to click"

        positions.click_view_role(index=0)
        positions.switch_to_new_tab()
        positions.wait_for_url_contains(Config.LEVER_DOMAIN)

        current_url = positions.driver.current_url
        assert Config.LEVER_DOMAIN in current_url, (
            f"Expected redirect to {Config.LEVER_DOMAIN}, got: {current_url}"
        )
