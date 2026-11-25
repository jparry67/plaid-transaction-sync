"""Plaid API client initialization and helper functions."""

from datetime import date, timedelta

from plaid import ApiClient, Configuration
from plaid.api.plaid_api import PlaidApi
from plaid.model.country_code import CountryCode
from plaid.model.item_public_token_exchange_request import ItemPublicTokenExchangeRequest
from plaid.model.link_token_create_request import LinkTokenCreateRequest
from plaid.model.products import Products
from plaid.model.transactions_get_request import TransactionsGetRequest

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
        "PLAID_ENV must be one of: sandbox, production. "
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
_plaid_api = PlaidApi(_plaid_client)

print(f"Plaid client initialized (env: {_PLAID_ENV}, host: {_config.host})")

_PLAID_CLIENT_USER_ID = f"plaid-sync-{_PLAID_ENV}"
_resp = _plaid_api.user_create({
    "client_user_id": _PLAID_CLIENT_USER_ID,
    "client_id": _PLAID_CLIENT_ID,
    "secret": _PLAID_SECRET,
})
_PLAID_USER_OBJ_ID = _resp.user_id
print(f"Plaid user created: {_PLAID_USER_OBJ_ID}")


def get_plaid_client():
    """Return the pre-initialized Plaid API (v43+ API object)."""
    return _plaid_api


def create_link_token():
    """Create a Plaid link token and return it as a dict."""
    request_obj = LinkTokenCreateRequest(
        client_name="Plaid Transaction Sync",
        language="en",
        country_codes=[CountryCode("US")],
        products=[Products("transactions")],
        client_id=_PLAID_CLIENT_ID,
        secret=_PLAID_SECRET,
        user_id=_PLAID_USER_OBJ_ID,
    )
    response = get_plaid_client().link_token_create(request_obj)
    return {"link_token": response.link_token}


def exchange_public_token(public_token):
    """Exchange a Plaid public_token for a permanent access_token."""
    request_obj = ItemPublicTokenExchangeRequest(
        public_token=public_token,
        client_id=_PLAID_CLIENT_ID,
        secret=_PLAID_SECRET,
    )
    response = get_plaid_client().item_public_token_exchange(request_obj)
    return response.access_token, response.item_id


def get_transactions(access_token, days=30, account_ids=None):
    """Retrieve transactions within the last N days (default 30)
    using /transactions/get with explicit start/end dates.

    *account_ids* can be used server-side to filter to specific
    accounts within an item (Plaid returns all accounts for an
    item under a single access_token by default).

    Returns a list of transaction dicts.
    """
    end_date = date.today()
    start_date = end_date - timedelta(days=days)
    options = {"count": 500}
    if account_ids is not None:
        options["account_ids"] = account_ids
    request_obj = TransactionsGetRequest(
        access_token=access_token,
        start_date=start_date,
        end_date=end_date,
        options=options,
        client_id=_PLAID_CLIENT_ID,
        secret=_PLAID_SECRET,
    )
    response = get_plaid_client().transactions_get(request_obj)
    return response.transactions or []
