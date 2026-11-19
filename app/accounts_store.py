"""Account storage backed by a local JSON file."""

import json
import os

from encryption import encrypt, decrypt

_FILE_PATH = os.path.join(os.path.dirname(__file__), "accounts.json")
_accounts = []


def _save_accounts(accounts):
    """Persist accounts to disk."""
    with open(_FILE_PATH, "w") as f:
        json.dump(accounts, f, indent=2)


def load_accounts():
    """Load accounts from disk into memory."""
    global _accounts
    if os.path.exists(_FILE_PATH):
        with open(_FILE_PATH, "r") as f:
            _accounts = json.load(f)
    else:
        _accounts = []
    print(f"Loaded {len(_accounts)} account(s) from {_FILE_PATH}")


def add_account(account):
    """Add a single account, encrypting the access token before persisting."""
    if "access_token" in account:
        account["access_token"] = encrypt(account["access_token"])
    _accounts.append(account)
    _save_accounts(_accounts)


def get_accounts():
    """Return all stored accounts with decrypted access tokens."""
    result = []
    for account in _accounts:
        entry = dict(account)
        if "access_token" in entry:
            entry["access_token"] = decrypt(entry["access_token"])
        result.append(entry)
    return result
