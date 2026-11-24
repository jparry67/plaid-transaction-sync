"""Transaction sync queue and history."""

from collections import deque
import threading
import time
from datetime import datetime, timezone

_sync_queue = deque()
_sync_history = []
_sync_counter = 0

def _ts():
    """Return an ISO-8601 UTC timestamp string."""
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def _log_entry(message):
    """Wrap a log message with a timestamp."""
    return {"message": message, "timestamp": _ts()}


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
    from accounts_store import get_accounts_with_tokens
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
    """Simulate syncing a single account with status updates.

    1. Status: "sync starting"  → sleep 5s
    2. Status: "sync in progress"  → sleep 5s
    3. Status: "sync complete", success, complete  → done
    """
    entry = _start_sync_for(account_id)

    time.sleep(5)

    entry["logs"].append(_log_entry("sync in progress"))

    time.sleep(5)

    entry["success"] = True
    entry["logs"].append(_log_entry("sync complete"))
    entry["complete"] = True


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
    return entry
