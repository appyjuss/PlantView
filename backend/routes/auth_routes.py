from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address
import datetime

from ..core import storage
from ..core import auth as core_auth

auth_bp = Blueprint('auth', __name__)

# Create limiter instance - will be initialized in main.py
limiter = Limiter(
    key_func=get_remote_address,
    default_limits=["200 per day", "50 per hour"],
    storage_uri="memory://"
)


@auth_bp.route('/api/auth/signup', methods=['POST'])
@limiter.limit("5 per hour")
def signup():
    """Register a new user with email and password."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    # Validate email format
    if not core_auth.validate_email(email):
        return jsonify({'error': 'Invalid email format'}), 400

    # Validate password strength
    is_valid, message = core_auth.validate_password_strength(password)
    if not is_valid:
        return jsonify({'error': message}), 400

    users = storage.load_users()
    if email in users:
        return jsonify({'error': 'User already exists'}), 409

    user_id = str(len(users) + 1)
    users[email] = {
        'id': user_id,
        'email': email,
        'password': generate_password_hash(password),
        'created_at': datetime.datetime.now(datetime.timezone.utc).isoformat(),
        'failed_login_attempts': 0,
        'locked_until': None
    }
    storage.save_users(users)

    access_token = core_auth.create_jwt_token(user_id, email, token_type='access')
    refresh_token = core_auth.create_jwt_token(user_id, email, token_type='refresh')
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user_id, 'email': email}
    }), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
@limiter.limit("10 per hour")
def login():
    """Authenticate user and return access and refresh tokens."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    users = storage.load_users()
    user = users.get(email)

    # Check if account is locked
    if user and user.get('locked_until'):
        lock_until = datetime.datetime.fromisoformat(user['locked_until'])
        if datetime.datetime.now(datetime.timezone.utc) < lock_until:
            return jsonify({
                'error': 'Account temporarily locked. Try again later.'
            }), 429

    if not user or not check_password_hash(user['password'], password):
        # Increment failed attempts
        if user:
            user['failed_login_attempts'] = user.get('failed_login_attempts', 0) + 1
            # Lock account after 5 failed attempts for 15 minutes
            if user['failed_login_attempts'] >= 5:
                user['locked_until'] = (
                    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
                ).isoformat()
            storage.save_users(users)
        return jsonify({'error': 'Invalid email or password'}), 401

    # Reset failed attempts on successful login
    user['failed_login_attempts'] = 0
    user['locked_until'] = None
    storage.save_users(users)

    access_token = core_auth.create_jwt_token(user['id'], email, token_type='access')
    refresh_token = core_auth.create_jwt_token(user['id'], email, token_type='refresh')
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user['id'], 'email': email}
    }), 200


@auth_bp.route('/api/auth/refresh', methods=['POST'])
@limiter.limit("30 per hour")
def refresh():
    """Refresh access token using refresh token."""
    data = request.get_json()
    if not data or not data.get('refresh_token'):
        return jsonify({'error': 'Refresh token required'}), 400

    refresh_token = data.get('refresh_token')
    payload = core_auth.verify_jwt_token(refresh_token, expected_type='refresh')
    
    if not payload:
        return jsonify({'error': 'Invalid or expired refresh token'}), 401

    user_id = payload.get('user_id')
    email = payload.get('email')
    
    access_token = core_auth.create_jwt_token(user_id, email, token_type='access')
    
    return jsonify({'access_token': access_token}), 200


@auth_bp.route('/api/auth/verify', methods=['GET'])
@core_auth.require_auth
def verify():
    """Verify current authentication token and return user info."""
    return jsonify({
        'user': {
            'id': request.user_id,
            'email': request.user_email
        }
    }), 200


@auth_bp.route('/api/auth/logout', methods=['POST'])
@core_auth.require_auth
def logout():
    """Logout user (token invalidation handled client-side)."""
    return jsonify({'message': 'Logged out successfully'}), 200
