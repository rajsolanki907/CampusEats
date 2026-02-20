import os
from typing import List

"""
Central configuration for the CampusEats backend.

Values can be overridden using environment variables in a local `.env` file
(when using tools like `uvicorn` with `python-dotenv`) or in your deployment
environment.
"""


def _get_list_from_env(var_name: str, default: str) -> List[str]:
    raw = os.getenv(var_name, default)
    parts = [item.strip() for item in raw.split(",")]
    return [p for p in parts if p]


# Database
DATABASE_URL: str = os.getenv("DATABASE_URL", "sqlite:///./campus_eats.db")

# Security
SECRET_KEY: str = os.getenv("SECRET_KEY", "CHANGE_ME_IN_PRODUCTION")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

# CORS / frontend access
CORS_ORIGINS: List[str] = _get_list_from_env("CORS_ORIGINS", "*")

