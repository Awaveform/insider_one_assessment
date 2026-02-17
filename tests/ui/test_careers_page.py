import pytest

from pages.home_page import HomePage
from pages.careers_page import CareersPage
from pages.open_positions_page import OpenPositionsPage
from config.config import Config


@pytest.mark.ui
class TestCareersFlow:
    """Steps 2-3: Navigate to QA careers, filter jobs, verify listings."""

    def test_navigate_to_qa_careers_and_click_see_all_jobs(self, driver):
        """Go to QA careers page, click 'See all QA jobs', verify open positions page loads."""
        home = HomePage(driver)
        home.open_home()
        home.accept_cookies_if_present()

        careers = CareersPage(driver)
        careers.open_qa_careers()
        assert careers.is_page_title_displayed(), "Careers page title not displayed"

        careers.click_see_all_qa_jobs()

    def test_filter_jobs_by_location_and_department(self, driver):
        """Filter jobs by Istanbul, Turkey and Quality Assurance, verify job list appears."""
        home = HomePage(driver)
        home.open_home()
        home.accept_cookies_if_present()

        careers = CareersPage(driver)
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()

        positions = OpenPositionsPage(driver)
        positions.filter_by_location("Istanbul, Turkey")
        positions.filter_by_department("Quality Assurance")

        assert positions.is_job_list_present(), "No job listings found after filtering"

    def test_all_jobs_position_contains_quality_assurance(self, driver):
        """Every listed job's Position should contain 'Quality Assurance'."""
        home = HomePage(driver)
        home.open_home()
        home.accept_cookies_if_present()

        careers = CareersPage(driver)
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()

        positions = OpenPositionsPage(driver)
        positions.filter_by_location("Istanbul, Turkey")
        positions.filter_by_department("Quality Assurance")

        job_positions = positions.get_job_positions()
        assert len(job_positions) > 0, "No job positions found"
        for pos in job_positions:
            assert "Quality Assurance" in pos, (
                f"Job position '{pos}' does not contain 'Quality Assurance'"
            )

    def test_all_jobs_department_contains_quality_assurance(self, driver):
        """Every listed job's Department should contain 'Quality Assurance'."""
        home = HomePage(driver)
        home.open_home()
        home.accept_cookies_if_present()

        careers = CareersPage(driver)
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()

        positions = OpenPositionsPage(driver)
        positions.filter_by_location("Istanbul, Turkey")
        positions.filter_by_department("Quality Assurance")

        departments = positions.get_job_departments()
        assert len(departments) > 0, "No job departments found"
        for dept in departments:
            assert "Quality Assurance" in dept, (
                f"Job department '{dept}' does not contain 'Quality Assurance'"
            )

    def test_all_jobs_location_contains_istanbul_turkey(self, driver):
        """Every listed job's Location should contain 'Istanbul, Turkey'."""
        home = HomePage(driver)
        home.open_home()
        home.accept_cookies_if_present()

        careers = CareersPage(driver)
        careers.open_qa_careers()
        careers.click_see_all_qa_jobs()

        positions = OpenPositionsPage(driver)
        positions.filter_by_location("Istanbul, Turkey")
        positions.filter_by_department("Quality Assurance")

        locations = positions.get_job_locations()
        assert len(locations) > 0, "No job locations found"
        for loc in locations:
            assert "Istanbul, Turkey" in loc, (
                f"Job location '{loc}' does not contain 'Istanbul, Turkey'"
            )
