class Config:
    """Central configuration for all test modules."""

    # UI Test URLs
    INSIDER_HOME_URL = "https://insiderone.com/"
    INSIDER_CAREERS_QA_URL = "https://insiderone.com/careers/quality-assurance/"
    INSIDER_OPEN_POSITIONS_URL = "https://insiderone.com/careers/open-positions/"

    # API Test URLs
    PETSTORE_BASE_URL = "https://petstore.swagger.io/v2"

    # Load Test URLs
    N11_BASE_URL = "https://www.n11.com"

    # Timeouts (seconds)
    DEFAULT_TIMEOUT = 15
    SHORT_TIMEOUT = 5
    LONG_TIMEOUT = 30

    # Browser defaults
    DEFAULT_BROWSER = "chrome"
    WINDOW_WIDTH = 1920
    WINDOW_HEIGHT = 1080

    # Lever application form domain (for redirect verification)
    LEVER_DOMAIN = "jobs.lever.co"
