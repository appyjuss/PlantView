import os
import requests
import json

DB_FILE = os.getenv('DB_FILE', 'users.json')

SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_KEY = os.getenv('SUPABASE_SERVICE_KEY')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'uploads')

def supabase_upload_file(file_stream, filename, content_type, user_id):
    """
    Uploads a file to Supabase Storage bucket with private access.
    Returns the file key or None on error.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{user_id}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_KEY}",
        "Content-Type": content_type
    }
    resp = requests.post(upload_url, headers=headers, data=file_stream)
    if resp.status_code in (200, 201):
        return f"{user_id}/{filename}"
    return None

def supabase_get_signed_url(file_key, expires_in=3600):
    """
    Generates a signed URL for private file access from Supabase Storage.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        return None
    url = f"{SUPABASE_URL}/storage/v1/object/sign/{SUPABASE_BUCKET}/{file_key}?expiresIn={expires_in}"
    headers = {"Authorization": f"Bearer {SUPABASE_SERVICE_KEY}"}
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('signedURL')
    return None


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
