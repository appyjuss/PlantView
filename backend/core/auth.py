import jwt
from datetime import datetime, timedelta, timezone
from functools import wraps
from flask import request, jsonify, current_app


def create_jwt_token(user_id, email):
    """Create a JWT token using app config for algorithm/expiration."""
    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    exp_hours = int(current_app.config.get('JWT_EXPIRATION_HOURS', 24))
    secret = current_app.config.get('SECRET_KEY')

    payload = {
        'user_id': user_id,
        'email': email,
        # integer epoch seconds for compatibility
        'iat': int(datetime.now(timezone.utc).timestamp()),
        'exp': int((datetime.now(timezone.utc) + timedelta(hours=exp_hours)).timestamp())
    }
    token = jwt.encode(payload, secret, algorithm=alg)
    return token


def verify_jwt_token(token):
    """Verify and decode a JWT using the app SECRET_KEY."""
    secret = current_app.config.get('SECRET_KEY')
    alg = current_app.config.get('JWT_ALGORITHM', 'HS256')
    try:
        payload = jwt.decode(token, secret, algorithms=[alg])
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

        payload = verify_jwt_token(token)
        if not payload:
            return jsonify({'error': 'Invalid or expired token'}), 401

        # Attach user info to request for downstream handlers
        request.user_id = payload.get('user_id')
        request.user_email = payload.get('email')
        return f(*args, **kwargs)

    return decorated
