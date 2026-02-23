import pytest

from config.config import settings


@pytest.mark.ui
class TestQACareersFlow:
    """End-to-end UI tests for the Insider One homepage and QA job flow."""

    def test_homepage_loads_and_renders_main_blocks(self, home) -> None:
        """Verify the homepage loads at the expected URL and all main sections are visible."""
        home.open_home()

        assert (settings.insider_home_url ==
                (current_url := home.get_current_url())), (
            f"Expected {settings.insider_home_url} URL, got: {current_url}"
        )

        assert home.is_cookies_modal_displayed(), \
            "Cookie consent banner is not visible"

        home.accept_cookies()

        assert (
            report := home.check_main_blocks()).ok(), (
                "Homepage structure validation failed.\n\n" +
                report.to_message()
        )

    def test_navigate_to_qa_careers_and_filter_jobs(
            self, careers, positions,
    ) -> None:
        """
        Navigate to the QA careers page, open all jobs, and filter by
        Istanbul, Turkiye.
        """
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()
        positions.filter_by_location(location=positions.ISTANBUL_TURKIYE)
        is_job_list_displayed = (
            positions.wait_until_positions_filtered_by_location(
                location=positions.ISTANBUL_TURKIYE
            ))
        assert is_job_list_displayed, (
            f"Job list is empty or was not found by location "
            f"'{positions.ISTANBUL_TURKIYE}'"
        )

    def test_filtered_jobs_match_attributes(self, positions) -> None:
        """
        Verify each visible job listing has the expected title,
        department, and location.
        """
        job_titles = positions.get_listed_positions_titles()
        job_departments = positions.get_listed_positions_departments()
        job_locations = positions.get_listed_positions_locations()

        for title in job_titles:
            assert positions.QUALITY_ASSURANCE in title, (
                f"Title '{title}' does not contain "
                f"'{positions.QUALITY_ASSURANCE}'"
            )
        for department in job_departments:
            assert positions.QUALITY_ASSURANCE == department, (
                f"Department '{department}' != "
                f"expected '{positions.QUALITY_ASSURANCE}'"
            )
        for location in job_locations:
            assert positions.ISTANBUL_TURKIYE == location, (
                f"Location '{location}' != "
                f"expected '{positions.ISTANBUL_TURKIYE}'"
            )

    def test_view_role_redirects_to_lever(self, positions) -> None:
        """
        Click 'View Role' on the first job and verify the redirect goes to
        Lever.
        """
        positions.click_view_role(index=0)
        positions.switch_to_new_tab()
        positions.wait_for_url_contains(settings.lever_domain)

        current_url = positions.driver.current_url
        assert settings.lever_domain in current_url, (
            f"Expected redirect to {settings.lever_domain}, got: {current_url}"
        )
