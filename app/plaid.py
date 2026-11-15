"""Plaid API client initialization."""

from plaid import ApiClient, Configuration

import os
from dotenv import load_dotenv

load_dotenv()

_ENV_MAP = {
    "sandbox": "https://sandbox.plaid.com",
    "development": "https://development.plaid.com",
    "production": "https://production.plaid.com",
}

_PLAID_ENV = os.getenv("PLAID_ENV")
if _PLAID_ENV not in _ENV_MAP:
    raise RuntimeError(
        "PLAID_ENV must be one of: sandbox, development, production. "
        f"Got: {_PLAID_ENV!r}"
    )

_PLAID_CLIENT_ID = os.getenv("PLAID_CLIENT_ID")
if _PLAID_CLIENT_ID is None:
    raise RuntimeError(
        "PLAID_CLIENT_ID is not set. "
        "Add it to your .env file."
    )

_PLAID_SECRET = os.getenv("PLAID_SECRET")
if _PLAID_SECRET is None:
    raise RuntimeError(
        "PLAID_SECRET is not set. "
        "Add it to your .env file."
    )

_config = Configuration(host=_ENV_MAP[_PLAID_ENV])
_config.api_key = {"PlaidAPI": f"{_PLAID_CLIENT_ID}:{_PLAID_SECRET}"}

_plaid_client = ApiClient(_config)

print(f"Plaid client initialized (env: {_PLAID_ENV}, host: {_config.host})")


def get_plaid_client():
    """Return the pre-initialized Plaid API client."""
    return _plaid_client
