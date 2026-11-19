"""Account storage backed by a local JSON file."""

import json
import os

from encryption import encrypt, decrypt

_FILE_PATH = "accounts.json"
_accounts = []

# Load accounts from disk on first import
if os.path.exists(_FILE_PATH):
    with open(_FILE_PATH, "r") as f:
        _accounts = json.load(f)
else:
    _accounts = []
print(f"Loaded {len(_accounts)} account(s) from {_FILE_PATH}")


def _save_accounts(accounts):
    """Persist accounts to disk."""
    with open(_FILE_PATH, "w") as f:
        json.dump(accounts, f, indent=2)


def add_account(account):
    """Add a single account, encrypting the access token before persisting."""
    if "access_token" in account:
        account["access_token"] = encrypt(account["access_token"])
    _accounts.append(account)
    _save_accounts(_accounts)


def get_accounts_with_tokens():
    """Return all stored accounts with decrypted access tokens."""
    result = []
    for account in _accounts:
        entry = dict(account)
        if "access_token" in entry:
            entry["access_token"] = decrypt(entry["access_token"])
        result.append(entry)
    return result


def get_account_summaries():
    """Return a visibility-friendly list with institution, name, mask, and subtype."""
    return [
        {
            "institution": a.get("institution"),
            "name": a.get("name"),
            "mask": a.get("mask"),
            "subtype": a.get("subtype"),
        }
        for a in _accounts
    ]
