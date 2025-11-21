import os
import json

DB_FILE = os.getenv('DB_FILE', 'users.json')


def load_users():
    """Load users from the file-based DB. Returns a dict."""
    if not os.path.exists(DB_FILE):
        return {}
    try:
        with open(DB_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def save_users(users):
    """Write users dict back to DB file."""
    with open(DB_FILE, 'w') as f:
        json.dump(users, f, indent=2)
