"""
Locust load test for n11.com search module.

Run headless (1 user, 30 seconds):
    locust -f tests/load/locustfile.py --host=https://www.n11.com \
        --users 1 --spawn-rate 1 --run-time 30s --headless

Run with web UI:
    locust -f tests/load/locustfile.py --host=https://www.n11.com
    # Then open http://localhost:8089
"""

import logging
import random

from locust import HttpUser, task, between, tag

logger = logging.getLogger(__name__)

SEARCH_TERMS = [
    "laptop",
    "telefon",
    "kulaklık",
    "samsung",
    "ayakkabı",
]

DEFAULT_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


class N11SearchUser(HttpUser):
    """Simulates a user searching for products on n11.com."""

    wait_time = between(1, 3)
    host = "https://www.n11.com"

    def on_start(self):
        """Load the homepage first (simulates a real user session)."""
        with self.client.get(
            "/",
            name="GET / (homepage)",
            catch_response=True,
            headers=DEFAULT_HEADERS,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Homepage returned {response.status_code}")

    @task(3)
    @tag("search")
    def search_product(self):
        """Simulate typing a search query and submitting."""
        query = random.choice(SEARCH_TERMS)
        with self.client.get(
            "/arama",
            params={"q": query},
            name="GET /arama?q=[search_term]",
            catch_response=True,
            headers=DEFAULT_HEADERS,
        ) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 403:
                response.failure("Blocked by bot detection (403)")
            else:
                response.failure(f"Search returned {response.status_code}")

    @task(1)
    @tag("search", "autocomplete")
    def search_autocomplete(self):
        """Simulate the autocomplete/suggestion AJAX call with partial query."""
        partial = random.choice(SEARCH_TERMS)[:3]
        with self.client.get(
            "/arama",
            params={"q": partial},
            name="GET /arama?q=[partial] (autocomplete)",
            catch_response=True,
            headers=DEFAULT_HEADERS,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Autocomplete returned {response.status_code}")

    @task(2)
    @tag("listing")
    def browse_listing_page(self):
        """Simulate browsing a search result listing page (page 2)."""
        query = random.choice(SEARCH_TERMS)
        with self.client.get(
            "/arama",
            params={"q": query, "pg": 2},
            name="GET /arama?q=[term]&pg=2 (page 2)",
            catch_response=True,
            headers=DEFAULT_HEADERS,
        ) as response:
            if response.status_code == 200:
                response.success()
            else:
                response.failure(f"Listing page returned {response.status_code}")
