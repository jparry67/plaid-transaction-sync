"""Account storage backed by a local JSON file."""

from encryption import encrypt, decrypt
from store import _load_or_init, save

_FILE_PATH = "accounts.json"
_accounts = _load_or_init(_FILE_PATH, [])


def _save_accounts(accounts):
    """Persist accounts to disk."""
    save(_FILE_PATH, accounts)


def add_account(account):
    """Add a single account, encrypting the access token before persisting."""
    if "access_token" in account:
        account["access_token"] = encrypt(account["access_token"])
    _accounts.append(account)
    _save_accounts(_accounts)


def remove_account(account_id):
    """Remove a single account by account_id and save."""
    before = len(_accounts)
    _accounts[:] = [a for a in _accounts if a.get("account_id") != account_id]
    if len(_accounts) != before:
        _save_accounts(_accounts)
        print(f"Removed account {account_id}")


def clear_accounts():
    """Remove all accounts and save."""
    _accounts.clear()
    _save_accounts(_accounts)
    print("Cleared all accounts")


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
    """Return a visibility-friendly list with institution, name, mask, subtype, and account_id."""
    return [
        {
            "account_id": a.get("account_id"),
            "institution": a.get("institution"),
            "name": a.get("name"),
            "mask": a.get("mask"),
            "subtype": a.get("subtype"),
        }
        for a in _accounts
    ]
