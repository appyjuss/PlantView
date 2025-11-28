import os
import logging
import requests
from .models import db, User, UploadRecord

logger = logging.getLogger(__name__)

# Compatibility constant used by legacy tests that expect a file-backed
# users store. The application uses the database, but tests may set
# `storage.USERS_FILE` to point at a temp file — provide a default.
USERS_FILE = os.getenv('USERS_FILE', None)

# Use the Supabase service role key name for server-side operations
SUPABASE_URL = os.getenv('SUPABASE_URL')
SUPABASE_SERVICE_ROLE_KEY = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
SUPABASE_BUCKET = os.getenv('SUPABASE_BUCKET', 'uploads')


def supabase_upload_file(file_data, filename, content_type, user_id):
    """
    Uploads a file to Supabase Storage bucket with private access.
    
    Args:
        file_data: File content as bytes
        filename: Name of the file
        content_type: MIME type of the file
        user_id: ID of the user uploading the file
    
    Returns:
        str or None: The file key on success, None on error.
    """
    # Resolve supabase config at call time (allow app config or env to provide values)
    try:
        from flask import current_app
        resolved_url = os.getenv('SUPABASE_URL') or current_app.config.get('SUPABASE_URL')
        resolved_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or current_app.config.get('SUPABASE_SERVICE_KEY') or current_app.config.get('SUPABASE_SERVICE_ROLE_KEY')
    except Exception:
        resolved_url = os.getenv('SUPABASE_URL')
        resolved_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not resolved_url or not resolved_key:
        logger.warning("Supabase upload attempted but SUPABASE_URL or SERVICE_ROLE_KEY not set")
        return None

    # Resolve bucket at call time too (allow override via app config)
    try:
        from flask import current_app
        resolved_bucket = os.getenv('SUPABASE_BUCKET') or current_app.config.get('SUPABASE_BUCKET', SUPABASE_BUCKET)
    except Exception:
        resolved_bucket = os.getenv('SUPABASE_BUCKET') or SUPABASE_BUCKET

    upload_url = f"{resolved_url}/storage/v1/object/{resolved_bucket}/{user_id}/{filename}"
    # Log masked info about the resolved key to catch truncation/mismatch issues
    try:
        k = resolved_key
        logger.warning("Using Supabase key: present=%s len=%s suffix=%s", bool(k), len(k), (k[-8:] if k and len(k) >= 8 else k))
    except Exception:
        logger.exception("Failed to log Supabase key metadata")

    headers = {
        "Authorization": f"Bearer {resolved_key}",
        "Content-Type": content_type
    }
    # Allow upsert/overwrite when uploading same filename if enabled via env var
    upsert_enabled = os.getenv('SUPABASE_UPSERT', 'true').lower() in ('1', 'true', 'yes')
    if upsert_enabled:
        headers['x-upsert'] = 'true'
    try:
        # `file_data` is expected to be bytes or a file-like object (we pass bytes from the route)
        resp = requests.post(upload_url, headers=headers, data=file_data, timeout=30)
    except Exception as e:
        logger.exception("Exception when POSTing to Supabase upload URL=%s for user=%s filename=%s", upload_url, user_id, filename)
        return None

    if resp.status_code in (200, 201):
        return f"{user_id}/{filename}"

    # Log failure to application logger (no file writes during cleanup)
    logger.error("Supabase upload failed: url=%s status=%s body=%s", upload_url, resp.status_code, (resp.text or resp.content))
    # If upsert is enabled and server responded 409, treat as success
    if resp.status_code == 409 and upsert_enabled:
        logger.warning("Supabase returned 409 Duplicate for %s; treating as success (upsert enabled)", upload_url)
        return f"{user_id}/{filename}"
    return None


def supabase_get_signed_url(file_key, expires_in=3600):
    """
    Generates a signed URL for private file access from Supabase Storage.
    """
    # Resolve config at call time
    try:
        from flask import current_app
        resolved_url = os.getenv('SUPABASE_URL') or current_app.config.get('SUPABASE_URL')
        resolved_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY') or current_app.config.get('SUPABASE_SERVICE_KEY') or current_app.config.get('SUPABASE_SERVICE_ROLE_KEY')
    except Exception:
        resolved_url = os.getenv('SUPABASE_URL')
        resolved_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')

    if not resolved_url or not resolved_key:
        logger.warning("Supabase signed URL requested but SUPABASE_URL or SERVICE_ROLE_KEY not set")
        return None

    # Resolve bucket at call time (mirror behavior in upload)
    try:
        from flask import current_app
        resolved_bucket = os.getenv('SUPABASE_BUCKET') or current_app.config.get('SUPABASE_BUCKET', SUPABASE_BUCKET)
    except Exception:
        resolved_bucket = os.getenv('SUPABASE_BUCKET') or SUPABASE_BUCKET

    url = f"{resolved_url}/storage/v1/object/sign/{resolved_bucket}/{file_key}?expiresIn={expires_in}"
    headers = {"Authorization": f"Bearer {resolved_key}"}
    try:
        resp = requests.post(url, headers=headers, timeout=30)
    except Exception:
        logger.exception("Exception when requesting signed URL for key=%s", file_key)
        return None

    # Log detailed response on failure to help debugging
    if resp.status_code == 200:
        try:
            data = resp.json()
            return data.get('signedURL')
        except Exception:
            logger.exception("Failed to parse JSON signed URL response for key=%s: %s", file_key, resp.text)
            return None

    logger.warning("Supabase signed URL request failed for key=%s status=%s body=%s", file_key, resp.status_code, (resp.text or resp.content))
    return None


def get_user_by_email(email: str):
    """Get user from database by email."""
    if USERS_FILE:
        users = load_users()
        u = users.get(email.lower())
        if not u:
            return None
        # Return a lightweight object compatible with User attributes used in routes/tests
        class FileUser:
            pass

        fu = FileUser()
        fu.id = u.get('id')
        fu.email = u.get('email')
        fu.password_hash = u.get('password_hash')
        fu.failed_login_attempts = int(u.get('failed_login_attempts') or 0)
        fu.locked_until = u.get('locked_until')
        return fu

    return User.query.filter_by(email=email.lower()).first()


def get_user_by_id(user_id: int):
    """Get user from database by ID."""
    return User.query.get(user_id)


def create_user(email: str, password_hash: str):
    """Create a new user in the database."""
    if USERS_FILE:
        users = load_users()
        # assign incremental id
        next_id = max((u.get('id', 0) for u in users.values()), default=0) + 1
        users[email.lower()] = {
            'id': next_id,
            'email': email.lower(),
            'password_hash': password_hash,
            'failed_login_attempts': 0,
            'locked_until': None,
            'created_at': None
        }
        save_users(users)

        class FileUser:
            pass

        fu = FileUser()
        fu.id = next_id
        fu.email = email.lower()
        fu.password_hash = password_hash
        fu.failed_login_attempts = 0
        fu.locked_until = None
        return fu

    user = User(email=email.lower(), password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user: User):
    """Update existing user in the database."""
    if USERS_FILE:
        users = load_users()
        email = getattr(user, 'email', None)
        if not email:
            return user
        entry = users.get(email.lower(), {})
        entry['failed_login_attempts'] = getattr(user, 'failed_login_attempts', entry.get('failed_login_attempts', 0))
        locked_until = getattr(user, 'locked_until', entry.get('locked_until'))
        if locked_until and hasattr(locked_until, 'isoformat'):
            entry['locked_until'] = locked_until.isoformat()
        else:
            entry['locked_until'] = locked_until
        users[email.lower()] = entry
        save_users(users)
        return user

    db.session.commit()
    return user


def get_all_users():
    """Get all users from database (admin use only)."""
    if USERS_FILE:
        users = load_users()
        return list(users.values())
    return User.query.all()


def create_upload_record(user_id: int, filename: str, file_path: str, detection_result=None):
    """Create an upload record linked to a user."""
    record = UploadRecord(
        user_id=user_id,
        filename=filename,
        file_path=file_path,
        detection_result=detection_result
    )
    db.session.add(record)
    db.session.commit()
    return record


def get_user_uploads(user_id: int):
    """Get all uploads for a specific user."""
    return UploadRecord.query.filter_by(user_id=user_id).all()


def get_upload_record(upload_id: int):
    """Get a specific upload record."""
    return UploadRecord.query.get(upload_id)


def load_users():
    """Compatibility loader used by tests.

    If `USERS_FILE` is set, load users from that JSON file. Otherwise,
    build a users dict from the database keyed by email.
    Returned structure matches the legacy file-backed format used in tests.
    """
    import json
    if USERS_FILE:
        try:
            with open(USERS_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}

    users = {}
    for u in User.query.all():
        users[u.email] = {
            'id': u.id,
            'email': u.email,
            'password_hash': u.password_hash,
            'failed_login_attempts': u.failed_login_attempts,
            'locked_until': u.locked_until.isoformat() if u.locked_until else None,
            'created_at': u.created_at.isoformat() if u.created_at else None
        }
    return users


def save_users(users_dict):
    """Compatibility saver used by tests.

    If `USERS_FILE` is set, write the JSON file. Otherwise, persist
    the relevant fields to the database (failed attempts and locked_until).
    """
    import json
    if USERS_FILE:
        with open(USERS_FILE, 'w', encoding='utf-8') as f:
            json.dump(users_dict, f)
        return

    # Persist to DB
    for email, info in users_dict.items():
        u = User.query.filter_by(email=email).first()
        if not u:
            continue
        if 'failed_login_attempts' in info:
            u.failed_login_attempts = int(info.get('failed_login_attempts') or 0)
        if 'locked_until' in info and info.get('locked_until'):
            try:
                from datetime import datetime
                u.locked_until = datetime.fromisoformat(info.get('locked_until'))
            except Exception:
                u.locked_until = None
        db.session.add(u)
    db.session.commit()
