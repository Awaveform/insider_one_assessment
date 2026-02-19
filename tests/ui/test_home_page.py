import pytest

from config.config import Config


@pytest.mark.ui
class TestHomePage:
    job_titles = []
    job_departments = []
    job_locations = []

    def test_homepage_loads_and_renders_main_blocks(self, home) -> None:
        home.open_home()

        assert (Config.INSIDER_HOME_URL ==
                (current_url := home.get_current_url())), (
            f"Expected {Config.INSIDER_HOME_URL} URL, got: {current_url}"
        )
        assert (
            report := home.check_main_blocks()).ok(), (
                "Homepage structure validation failed.\n\n" +
                report.to_message()
        )

        home.accept_cookies_if_present()  # guard for next steps

    def test_navigate_to_qa_careers_and_filter_jobs(
            self, careers, positions,
    ):
        """
        Go to QA careers page, click 'See all QA jobs', verify open
        positions page loads.
        """
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()
        positions.filter_by_location(location=positions.ISTANBUL_TURKIYE)
        is_job_list_displayed = (
            positions.wait_until_positions_filtered_by_location(
                location=positions.ISTANBUL_TURKIYE
            ))
        assert is_job_list_displayed, \
            (
                f"Job list is empty or was not found by location "
                f"'{positions.ISTANBUL_TURKIYE}'"
            )

    def test_filtered_jobs_match_attributes(self, positions):
        """
        Go to QA careers page, click 'See all QA jobs', verify open
        positions page loads.
        """
        job_titles = positions.get_listed_positions_titles()
        job_departments = positions.get_listed_positions_departments()
        job_locations = positions.get_listed_positions_locations()

        for title in job_titles:
            assert positions.QUALITY_ASSURANCE in title, \
                (
                    f"Title '{title}' does not contain "
                    f"{positions.QUALITY_ASSURANCE}"
                )
        for department in job_departments:
            assert positions.QUALITY_ASSURANCE == department, \
                (
                    f"Department '{department}' != "
                    f"expected '{positions.QUALITY_ASSURANCE}'"
                )
        for location in job_locations:
            assert positions.QUALITY_ASSURANCE == location, \
                (
                    f"Location '{location}' != "
                    f"expected '{positions.ISTANBUL_TURKIYE}'"
                )

    def test_view_role_redirects_to_lever(self, positions):
        positions.click_view_role(index=0)
        positions.switch_to_new_tab()
        positions.wait_for_url_contains(Config.LEVER_DOMAIN)

        current_url = positions.driver.current_url
        assert Config.LEVER_DOMAIN in current_url, (
            f"Expected redirect to {Config.LEVER_DOMAIN}, got: {current_url}"
        )
