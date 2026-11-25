"""Transaction sync queue and history."""

import csv
import os
from collections import deque
import threading
from datetime import datetime, timezone

from store import _load_or_init, save
from accounts import get_accounts_with_tokens
from plaid_client import get_transactions

_FILE_PATH = "sync_history.json"

_sync_queue = deque()
_sync_history = _load_or_init(_FILE_PATH, [])
_sync_counter = max((e.get("sync_id", 0) for e in _sync_history), default=0)


def _save_history():
    """Persist sync history to disk."""
    save(_FILE_PATH, _sync_history)


def _ts():
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log_entry(message):
    """Wrap a log message with a timestamp."""
    return {"message": message, "timestamp": _ts()}


def _normalize(string):
    """Normalize strings for filenames."""
    return "_".join(string.lower().strip().split())


def get_sync_history():
    """Return all completed/running syncs, plus any queued (pending) items."""
    result = list(_sync_history)
    for account_id in _sync_queue:
        result.append({
            "account_id": account_id,
            "logs": [],
            "success": False,
            "complete": False,
        })
    return result


def sync_all():
    """Add all account IDs to the queue and kick off processing in a background thread."""
    accounts = get_accounts_with_tokens()
    for acct in accounts:
        _sync_queue.append(acct.get("account_id"))
    _start_sync_in_background()


def sync_account(account_id):
    """Add a single account ID to the queue and kick off processing in a background thread."""
    _sync_queue.append(account_id)
    _start_sync_in_background()


def _start_sync_in_background():
    """Start a background thread to process the queue, so the API returns immediately."""
    t = threading.Thread(target=_start_sync, daemon=True)
    t.start()


def _start_sync():
    """Process the queue: bail out if a sync is running, otherwise process one item."""
    global _sync_queue

    if _is_sync_in_progress() or not _sync_queue:
        return

    account_id = _sync_queue.popleft()
    _sync(account_id)

    if _sync_queue:
        _start_sync()


def _sync(account_id):
    """Sync transactions for a single account.

    1. Status: "sync starting" (from _start_sync_for)
    2. Status: "sync in progress" with transaction count
    3. Status: "sync complete", success, complete  → done
    """

    entry = _start_sync_for(account_id)

    # Find the account's access token
    accounts = get_accounts_with_tokens()
    acct = next((a for a in accounts if a["account_id"] == account_id), None)
    if not acct:
        entry["logs"].append(_log_entry("error: account not found"))
        entry["complete"] = True
        _save_history()
        return

    try:
        trxs = get_transactions(acct["access_token"], days=30, account_ids=[account_id])
        transactions = []
        for transaction in trxs:
            transactions.append({
                "date": transaction["date"].strftime("%m/%d/%Y"),
                "description": transaction["name"],
                "amount": -1 * float(transaction["amount"]),
                "status": "Pending" if transaction["pending"] else "Posted"
            })
        entry["logs"].append(_log_entry(f"pulled {len(transactions)} transactions"))
        _write_transactions_csv(acct, transactions, entry)

    except Exception as e:
        entry["logs"].append(_log_entry(f"error: {e}"))
        entry["complete"] = True
        _save_history()

    entry["success"] = True
    entry["complete"] = True
    _save_history()


def _write_transactions_csv(acct, transactions, entry):
    """Write *transactions* to a dated CSV file under csv_transactions/.

    The file is named like ``{institution}_{name}_{mask}_{MM_DD_YYYY}.csv``.
    If there are no transactions the entry is logged but no file is created.
    """
    today = datetime.now()
    acct_file_name = (
        f"{_normalize(acct['institution'])}_"
        f"{_normalize(acct['name'])}_"
        f"{_normalize(acct['mask'])}_"
        f"{today.strftime('%m_%d_%Y')}.csv"
    )
    csv_dir = "csv_transactions"
    os.makedirs(csv_dir, exist_ok=True)
    csv_path = os.path.join(csv_dir, acct_file_name)

    if not transactions:
        entry["logs"].append(_log_entry("no transactions to write"))
        return

    fieldnames = transactions[0].keys()
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(transactions)
    entry["logs"].append(_log_entry(f"wrote {len(transactions)} transactions to {acct_file_name}"))
    _save_history()

def _trim_history():
    """Keep only the 30 most recent syncs."""
    while len(_sync_history) > 30:
        _sync_history.pop(0)
    _save_history()


def _is_sync_in_progress():
    """Return False if no history or last sync is complete; True otherwise."""
    if not _sync_history:
        return False
    return not _sync_history[-1]["complete"]


def _start_sync_for(account_id):
    """Create a new history object and set status to 'sync starting'."""
    global _sync_counter
    _sync_counter += 1
    entry = {
        "sync_id": _sync_counter,
        "account_id": account_id,
        "logs": [_log_entry("sync starting")],
        "success": False,
        "complete": False,
    }
    _sync_history.append(entry)
    _trim_history()
    return entry
