import os

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'webp'}
ALLOWED_MIME_TYPES = {'image/png', 'image/jpeg', 'image/jpg', 'image/webp'}

# Model configuration
MODEL_VERSION = os.getenv('MODEL_VERSION', 'resnet50-v1.0')
MAX_CONTENT_LENGTH = int(os.getenv('MAX_UPLOAD_SIZE', str(10 * 1024 * 1024)))  # 10MB default


def allowed_file(filename: str) -> bool:
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def validate_content_type(content_type: str) -> tuple[bool, str | None]:
    """Validate content type is an allowed image MIME type."""
    if not content_type or content_type not in ALLOWED_MIME_TYPES:
        return False, f"Invalid content type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
    return True, None


def validate_file_size(file, max_size: int = MAX_CONTENT_LENGTH) -> tuple[bool, int | str]:
    """Validate file size doesn't exceed limit. Returns (is_valid, size_or_error_message)."""
    file.seek(0, os.SEEK_END)
    size = file.tell()
    file.seek(0)  # Reset to start
    
    if size > max_size:
        return False, f"File size ({size} bytes) exceeds maximum allowed size ({max_size} bytes)"
    return True, size
