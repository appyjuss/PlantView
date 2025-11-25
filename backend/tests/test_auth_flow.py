"""
Comprehensive tests for the authentication flow.
Tests cover signup, login, token refresh, and protected endpoints.
"""
import pytest
import json
import os
import sys
from datetime import datetime, timedelta, timezone

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.main import app
from backend.core import storage
from backend.core import auth as core_auth


@pytest.fixture
def client():
    """Create a test client with a test database."""
    app.config['TESTING'] = True
    app.config['ENV'] = 'testing'
    app.config['RATELIMIT_ENABLED'] = False
    
    # Use test users file
    test_users_file = 'backend/tests/test_users.json'
    os.makedirs(os.path.dirname(test_users_file), exist_ok=True)
    
    # Mock the storage to use test file
    original_users_file = storage.USERS_FILE
    storage.USERS_FILE = test_users_file
    
    with app.test_client() as client:
        yield client
    
    # Cleanup
    storage.USERS_FILE = original_users_file
    if os.path.exists(test_users_file):
        os.remove(test_users_file)


@pytest.fixture
def clean_users():
    """Clean up users before each test."""
    test_users_file = 'backend/tests/test_users.json'
    if os.path.exists(test_users_file):
        os.remove(test_users_file)
    storage.USERS_FILE = test_users_file
    yield
    if os.path.exists(test_users_file):
        os.remove(test_users_file)


class TestSignup:
    """Test user signup endpoint."""
    
    def test_signup_success(self, client, clean_users):
        """Test successful signup with valid credentials."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
        assert 'id' in data['user']
    
    def test_signup_missing_email(self, client, clean_users):
        """Test signup fails without email."""
        response = client.post('/api/auth/signup', json={
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_signup_missing_password(self, client, clean_users):
        """Test signup fails without password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_signup_invalid_email(self, client, clean_users):
        """Test signup fails with invalid email format."""
        response = client.post('/api/auth/signup', json={
            'email': 'invalid-email',
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        assert 'Invalid email format' in response.get_json()['error']
    
    def test_signup_password_too_short(self, client, clean_users):
        """Test signup fails with password less than 8 characters."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Short1!'
        })
        
        assert response.status_code == 400
        assert 'at least 8 characters' in response.get_json()['error']
    
    def test_signup_password_missing_uppercase(self, client, clean_users):
        """Test signup fails without uppercase letter in password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'password123!'
        })
        
        assert response.status_code == 400
        assert 'uppercase' in response.get_json()['error']
    
    def test_signup_password_missing_digit(self, client, clean_users):
        """Test signup fails without digit in password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password!'
        })
        
        assert response.status_code == 400
        assert 'digit' in response.get_json()['error']
    
    def test_signup_password_missing_special_char(self, client, clean_users):
        """Test signup fails without special character in password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123'
        })
        
        assert response.status_code == 400
        assert 'special character' in response.get_json()['error']
    
    def test_signup_duplicate_user(self, client, clean_users):
        """Test signup fails when user already exists."""
        # First signup
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Second signup with same email
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password456!'
        })
        
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error']
    
    def test_signup_email_case_insensitive(self, client, clean_users):
        """Test that email signup is case-insensitive."""
        # Signup with lowercase
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Try signup with uppercase
        response = client.post('/api/auth/signup', json={
            'email': 'TEST@EXAMPLE.COM',
            'password': 'Password456!'
        })
        
        assert response.status_code == 409
        assert 'already exists' in response.get_json()['error']


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, clean_users):
        """Test successful login with valid credentials."""
        # Create user first
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Login
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'test@example.com'
    
    def test_login_missing_email(self, client, clean_users):
        """Test login fails without email."""
        response = client.post('/api/auth/login', json={
            'password': 'Password123!'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_login_missing_password(self, client, clean_users):
        """Test login fails without password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_login_nonexistent_user(self, client, clean_users):
        """Test login fails for non-existent user."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 401
        assert 'Invalid email or password' in response.get_json()['error']
    
    def test_login_wrong_password(self, client, clean_users):
        """Test login fails with wrong password."""
        # Create user
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Try login with wrong password
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == 401
        assert 'Invalid email or password' in response.get_json()['error']
    
    def test_login_resets_failed_attempts(self, client, clean_users):
        """Test that successful login resets failed login attempts."""
        # Create user
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Fail login several times
        for _ in range(3):
            client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'WrongPassword!'
            })
        
        # Successful login should reset counter
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 200
        
        # User data should have reset counter
        users = storage.load_users()
        assert users['test@example.com']['failed_login_attempts'] == 0


class TestAccountLockout:
    """Test account lockout mechanism after failed login attempts."""
    
    def test_account_lockout_after_failed_attempts(self, client, clean_users):
        """Test account is locked after 5 failed login attempts."""
        # Create user
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Make 5 failed login attempts
        for _ in range(5):
            client.post('/api/auth/login', json={
                'email': 'test@example.com',
                'password': 'WrongPassword!'
            })
        
        # Next login attempt should fail with lockout message
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123!'  # Even correct password fails
        })
        
        assert response.status_code == 429
        assert 'temporarily locked' in response.get_json()['error']
    
    def test_locked_account_unlocks_after_timeout(self, client, clean_users):
        """Test account unlocks after lockout period expires."""
        # Create user
        client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        # Lock the account manually
        users = storage.load_users()
        users['test@example.com']['failed_login_attempts'] = 5
        users['test@example.com']['locked_until'] = (
            datetime.now(timezone.utc) - timedelta(minutes=1)
        ).isoformat()
        storage.save_users(users)
        
        # Login should now work
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        
        assert response.status_code == 200


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client, clean_users):
        """Test successful token refresh."""
        # Signup to get refresh token
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        refresh_token = signup_response.get_json()['refresh_token']
        
        # Refresh the token
        response = client.post('/api/auth/refresh', json={
            'refresh_token': refresh_token
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_refresh_without_token(self, client, clean_users):
        """Test refresh fails without refresh token."""
        response = client.post('/api/auth/refresh', json={})
        
        assert response.status_code == 400
        assert 'Refresh token required' in response.get_json()['error']
    
    def test_refresh_with_invalid_token(self, client, clean_users):
        """Test refresh fails with invalid refresh token."""
        response = client.post('/api/auth/refresh', json={
            'refresh_token': 'invalid.token.here'
        })
        
        assert response.status_code == 401
        assert 'Invalid or expired refresh token' in response.get_json()['error']
    
    def test_refresh_with_access_token_fails(self, client, clean_users):
        """Test refresh fails when using access token instead of refresh token."""
        # Signup to get tokens
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        access_token = signup_response.get_json()['access_token']
        
        # Try to refresh with access token
        response = client.post('/api/auth/refresh', json={
            'refresh_token': access_token
        })
        
        assert response.status_code == 401
        assert 'Invalid or expired refresh token' in response.get_json()['error']


class TestVerifyToken:
    """Test token verification endpoint."""
    
    def test_verify_valid_token(self, client, clean_users):
        """Test verification with valid access token."""
        # Signup to get access token
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        access_token = signup_response.get_json()['access_token']
        
        # Verify token
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['email'] == 'test@example.com'
    
    def test_verify_missing_token(self, client, clean_users):
        """Test verify fails without token."""
        response = client.get('/api/auth/verify')
        
        assert response.status_code == 401
        assert 'Missing authorization token' in response.get_json()['error']
    
    def test_verify_invalid_token(self, client, clean_users):
        """Test verify fails with invalid token."""
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': 'Bearer invalid.token.here'}
        )
        
        assert response.status_code == 401
        assert 'Invalid or expired token' in response.get_json()['error']
    
    def test_verify_malformed_header(self, client, clean_users):
        """Test verify fails with malformed authorization header."""
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': 'InvalidFormat'}
        )
        
        assert response.status_code == 401
        assert 'Invalid authorization header' in response.get_json()['error']


class TestLogout:
    """Test logout endpoint."""
    
    def test_logout_success(self, client, clean_users):
        """Test successful logout."""
        # Signup to get token
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        access_token = signup_response.get_json()['access_token']
        
        # Logout
        response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        
        assert response.status_code == 200
        assert 'Logged out successfully' in response.get_json()['message']
    
    def test_logout_without_token(self, client, clean_users):
        """Test logout fails without token."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 401


class TestTokenValidation:
    """Test JWT token validation and expiration."""
    
    def test_access_token_has_correct_type(self, client, clean_users):
        """Test access token has correct token type."""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        access_token = signup_response.get_json()['access_token']
        
        # Decode token manually to check type
        payload = core_auth.verify_jwt_token(access_token, expected_type='access')
        assert payload is not None
        assert payload['type'] == 'access'
    
    def test_refresh_token_has_correct_type(self, client, clean_users):
        """Test refresh token has correct token type."""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        refresh_token = signup_response.get_json()['refresh_token']
        
        # Decode token manually to check type
        payload = core_auth.verify_jwt_token(refresh_token, expected_type='refresh')
        assert payload is not None
        assert payload['type'] == 'refresh'
    
    def test_token_contains_user_info(self, client, clean_users):
        """Test token contains user id and email."""
        signup_response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Password123!'
        })
        access_token = signup_response.get_json()['access_token']
        
        payload = core_auth.verify_jwt_token(access_token, expected_type='access')
        assert payload['user_id'] == payload['user_id']
        assert payload['email'] == 'test@example.com'


class TestCompleteAuthFlow:
    """Test complete authentication flow from signup to protected endpoint."""
    
    def test_complete_auth_flow(self, client, clean_users):
        """Test the complete authentication flow."""
        # Step 1: Signup
        signup_response = client.post('/api/auth/signup', json={
            'email': 'user@example.com',
            'password': 'SecurePass123!'
        })
        assert signup_response.status_code == 201
        signup_data = signup_response.get_json()
        access_token = signup_data['access_token']
        refresh_token = signup_data['refresh_token']
        
        # Step 2: Verify token immediately after signup
        verify_response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert verify_response.status_code == 200
        assert verify_response.get_json()['user']['email'] == 'user@example.com'
        
        # Step 3: Logout
        logout_response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        assert logout_response.status_code == 200
        
        # Step 4: Login again
        login_response = client.post('/api/auth/login', json={
            'email': 'user@example.com',
            'password': 'SecurePass123!'
        })
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        new_access_token = login_data['access_token']
        new_refresh_token = login_data['refresh_token']
        
        # Step 5: Refresh the access token
        refresh_response = client.post('/api/auth/refresh', json={
            'refresh_token': new_refresh_token
        })
        assert refresh_response.status_code == 200
        refreshed_token = refresh_response.get_json()['access_token']
        
        # Step 6: Verify with refreshed token
        verify_response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {refreshed_token}'}
        )
        assert verify_response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
