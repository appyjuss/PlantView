from flask import Blueprint, request, jsonify, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from sqlalchemy.exc import IntegrityError
import datetime

from ..core import storage
from ..core import auth as core_auth
from ..core.models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/signup', methods=['POST'])
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

    # Check if user exists
    if storage.get_user_by_email(email):
        return jsonify({'error': 'User already exists'}), 409

    try:
        # Create new user with hashed password
        user = storage.create_user(email, generate_password_hash(password))
        
        access_token = core_auth.create_jwt_token(user.id, email, token_type='access')
        refresh_token = core_auth.create_jwt_token(user.id, email, token_type='refresh')
        
        return jsonify({
            'access_token': access_token,
            'refresh_token': refresh_token,
            'user': {'id': user.id, 'email': user.email}
        }), 201
    except IntegrityError:
        db.session.rollback()
        return jsonify({'error': 'User already exists'}), 409
    except Exception as e:
        db.session.rollback()
        current_app.logger.error(f"Signup error: {str(e)}")
        return jsonify({'error': 'Internal server error'}), 500


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    """Authenticate user and return access and refresh tokens."""
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data.get('email', '').strip().lower()
    password = data.get('password', '')

    user = storage.get_user_by_email(email)

    # Check if account is locked
    if user and user.locked_until:
        lock_until = user.locked_until
        if isinstance(lock_until, str):
            lock_until = datetime.datetime.fromisoformat(lock_until)
        # Normalize naive datetimes to UTC-aware for safe comparison
        if lock_until.tzinfo is None:
            lock_until = lock_until.replace(tzinfo=datetime.timezone.utc)
        if datetime.datetime.now(datetime.timezone.utc) < lock_until:
            return jsonify({
                'error': 'Account temporarily locked. Try again later.'
            }), 429

    if not user or not check_password_hash(user.password_hash, password):
        # Increment failed attempts
        if user:
            user.failed_login_attempts = user.failed_login_attempts + 1
            # Lock account after 5 failed attempts for 15 minutes
            if user.failed_login_attempts >= 5:
                user.locked_until = (
                    datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=15)
                )
            storage.update_user(user)
        return jsonify({'error': 'Invalid email or password'}), 401

    # Reset failed attempts on successful login
    user.failed_login_attempts = 0
    user.locked_until = None
    storage.update_user(user)

    access_token = core_auth.create_jwt_token(user.id, email, token_type='access')
    refresh_token = core_auth.create_jwt_token(user.id, email, token_type='refresh')
    
    return jsonify({
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': {'id': user.id, 'email': user.email}
    }), 200


@auth_bp.route('/api/auth/refresh', methods=['POST'])
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
