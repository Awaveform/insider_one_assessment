import configparser
import os

from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# ---------------------------------------------------------------------------
# Resolve the .env path declared in pytest.ini
# ---------------------------------------------------------------------------
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_pytest_ini_path = os.path.join(_root, "pytest.ini")

_config = configparser.ConfigParser()
_config.read(_pytest_ini_path)

path_env_file = os.path.join(
    _root, _config.get("pytest", "env_file", fallback=".env").strip()
)

load_dotenv(path_env_file)


# ---------------------------------------------------------------------------
# Settings — single source of truth for the whole test suite
# ---------------------------------------------------------------------------
class Settings(BaseSettings):
    """Project-wide settings loaded from the .env file declared in pytest.ini."""

    # UI Test URLs
    insider_home_url: str
    insider_careers_qa_url: str
    insider_open_positions_url: str

    # API Test URLs
    petstore_base_url: str

    # Load Test URLs
    n11_base_url: str

    # Timeouts (seconds)
    default_timeout: int
    short_timeout: int
    long_timeout: int

    # Browser defaults
    default_browser: str
    window_width: int
    window_height: int

    # Lever application form domain (for redirect verification)
    lever_domain: str

    model_config = {
        "env_file": path_env_file,
        "env_file_encoding": "utf-8",
    }


# noinspection PyArgumentList
settings = Settings()
