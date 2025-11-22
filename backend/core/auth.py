import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app
import re


def validate_email(email):
    """Validate email format."""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email.strip()) is not None


def validate_password_strength(password):
    """Validate password strength. Returns tuple (is_valid, message)."""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    if len(password) > 128:
        return False, "Password must be less than 128 characters"
    if not any(char.isupper() for char in password):
        return False, "Password must contain at least one uppercase letter"
    if not any(char.isdigit() for char in password):
        return False, "Password must contain at least one digit"
    if not any(char in '!@#$%^&*()-_=+[]{}|;:,.<>?' for char in password):
        return False, "Password must contain at least one special character"
    return True, "Password is valid"


def create_jwt_token(user_id, email, token_type='access', expires_in_hours=None):
    """Create a JWT token using app config for algorithm/expiration.
    
    Args:
        user_id: User identifier
        email: User email
        token_type: 'access' or 'refresh'
        expires_in_hours: Override default expiration
    """
    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    secret = current_app.config.get('SECRET_KEY')
    
    if token_type == 'refresh':
        exp_hours = expires_in_hours or int(current_app.config.get('JWT_REFRESH_EXPIRATION_HOURS', 168))
    else:
        exp_hours = expires_in_hours or int(current_app.config.get('JWT_EXPIRATION_HOURS', 1))

    now = datetime.now(timezone.utc)
    payload = {
        'user_id': user_id,
        'email': email,
        'type': token_type,
        'iat': int(now.timestamp()),
        'exp': int((now + timedelta(hours=exp_hours)).timestamp())
    }
    token = jwt.encode(payload, secret, algorithm=alg)
    return token


def verify_jwt_token(token, expected_type='access'):
    """Verify and decode a JWT using the app SECRET_KEY.
    
    Args:
        token: JWT token string
        expected_type: Expected token type ('access' or 'refresh')
        
    Returns:
        Payload dict if valid, None otherwise
    """
    secret = current_app.config.get('SECRET_KEY')
    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(token, secret, algorithms=[alg])
        if payload.get('type') != expected_type:
            return None
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None


def require_auth(f):
    """Flask decorator that ensures a valid JWT is present in Authorization header."""
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        if 'Authorization' in request.headers:
            auth_header = request.headers['Authorization']
            try:
                token = auth_header.split(' ')[1]
            except IndexError:
                return jsonify({'error': 'Invalid authorization header'}), 401

        if not token:
            return jsonify({'error': 'Missing authorization token'}), 401

        payload = verify_jwt_token(token, expected_type='access')
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Attach user info to request for downstream handlers
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        return f(*args, **kwargs)

    return decorated
