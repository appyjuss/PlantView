import os
import requests
from .models import db, User, UploadRecord

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
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{SUPABASE_BUCKET}/{user_id}/{filename}"
    headers = {
        "Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}",
        "Content-Type": content_type
    }
    resp = requests.post(upload_url, headers=headers, data=file_data)
    if resp.status_code in (200, 201):
        return f"{user_id}/{filename}"
    return None


def supabase_get_signed_url(file_key, expires_in=3600):
    """
    Generates a signed URL for private file access from Supabase Storage.
    """
    if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
        return None
    url = f"{SUPABASE_URL}/storage/v1/object/sign/{SUPABASE_BUCKET}/{file_key}?expiresIn={expires_in}"
    headers = {"Authorization": f"Bearer {SUPABASE_SERVICE_ROLE_KEY}"}
    resp = requests.post(url, headers=headers)
    if resp.status_code == 200:
        data = resp.json()
        return data.get('signedURL')
    return None


def get_user_by_email(email: str):
    """Get user from database by email."""
    return User.query.filter_by(email=email.lower()).first()


def get_user_by_id(user_id: int):
    """Get user from database by ID."""
    return User.query.get(user_id)


def create_user(email: str, password_hash: str):
    """Create a new user in the database."""
    user = User(email=email.lower(), password_hash=password_hash)
    db.session.add(user)
    db.session.commit()
    return user


def update_user(user: User):
    """Update existing user in the database."""
    db.session.commit()
    return user


def get_all_users():
    """Get all users from database (admin use only)."""
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
