from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash

from ..core import storage
from ..core import auth as core_auth

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/api/auth/signup', methods=['POST'])
def signup():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data.get('email').strip().lower()
    password = data.get('password')

    if len(password) < 6:
        return jsonify({'error': 'Password must be at least 6 characters'}), 400

    users = storage.load_users()
    if email in users:
        return jsonify({'error': 'User already exists'}), 409

    user_id = str(len(users) + 1)
    users[email] = {
        'id': user_id,
        'email': email,
        'password': generate_password_hash(password),
        'created_at': __import__('datetime').datetime.now(__import__('datetime').timezone.utc).isoformat()
    }
    storage.save_users(users)

    token = core_auth.create_jwt_token(user_id, email)
    return jsonify({'token': token, 'user': {'id': user_id, 'email': email}}), 201


@auth_bp.route('/api/auth/login', methods=['POST'])
def login():
    data = request.get_json()
    if not data or not data.get('email') or not data.get('password'):
        return jsonify({'error': 'Email and password required'}), 400

    email = data.get('email').strip().lower()
    password = data.get('password')

    users = storage.load_users()
    user = users.get(email)

    if not user or not check_password_hash(user['password'], password):
        return jsonify({'error': 'Invalid email or password'}), 401

    token = core_auth.create_jwt_token(user['id'], email)
    return jsonify({'token': token, 'user': {'id': user['id'], 'email': email}}), 200
