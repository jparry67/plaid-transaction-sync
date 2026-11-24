"""Generic JSON-backed list store."""

import json
import os


def _load_or_init(file_path, empty):
    """Load a list from a JSON file, or return empty default."""
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
        print(f"Loaded {len(data)} record(s) from {file_path}")
        return data
    print(f"No {file_path} found; starting fresh.")
    return list(empty)


def save(file_path, data):
    """Persist a list to a JSON file."""
    with open(file_path, "w") as f:
        json.dump(data, f, indent=2)
