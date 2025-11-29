"""
Test suite for authentication endpoints with SQLAlchemy database.
Tests cover signup, login, token refresh, and account lockout.
"""
from datetime import timedelta

from backend.core.models import User
from backend.core import auth as core_auth


class TestSignup:
    """Test user signup endpoint."""
    
    def test_signup_success(self, client):
        """Test successful signup with valid credentials."""
        response = client.post('/api/auth/signup', json={
            'email': 'newuser@example.com',
            'password': 'ValidPassword123!'
        })
        
        assert response.status_code == 201
        data = response.get_json()
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['email'] == 'newuser@example.com'
        assert 'id' in data['user']
        assert isinstance(data['user']['id'], int)
    
    def test_signup_missing_email(self, client):
        """Test signup fails without email."""
        response = client.post('/api/auth/signup', json={
            'password': 'ValidPassword123!'
        })
        
        assert response.status_code == 400
        assert 'Email and password required' in response.get_json()['error']
    
    def test_signup_missing_password(self, client):
        """Test signup fails without password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        assert 'Email and password required' in response.get_json()['error']
    
    def test_signup_invalid_email_format(self, client):
        """Test signup fails with invalid email format."""
        response = client.post('/api/auth/signup', json={
            'email': 'not-an-email',
            'password': 'ValidPassword123!'
        })
        
        assert response.status_code == 400
        assert 'Invalid email format' in response.get_json()['error']
    
    def test_signup_password_too_short(self, client):
        """Test signup fails with short password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'Short1!'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_signup_password_no_uppercase(self, client):
        """Test signup fails without uppercase letter in password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'lowercase123!'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_signup_password_no_number(self, client):
        """Test signup fails without number in password."""
        response = client.post('/api/auth/signup', json={
            'email': 'test@example.com',
            'password': 'NoNumbers!'
        })
        
        assert response.status_code == 400
        assert 'error' in response.get_json()
    
    def test_signup_duplicate_email(self, client, authenticated_user):
        """Test signup fails when email already exists."""
        response = client.post('/api/auth/signup', json={
            'email': authenticated_user.email,
            'password': 'NewPassword123!'
        })
        
        assert response.status_code == 409
        assert 'User already exists' in response.get_json()['error']
    
    def test_signup_email_case_insensitive(self, client):
        """Test that email is case-insensitive for uniqueness."""
        # First signup
        response1 = client.post('/api/auth/signup', json={
            'email': 'TestUser@Example.com',
            'password': 'ValidPassword123!'
        })
        assert response1.status_code == 201
        
        # Second signup with different case
        response2 = client.post('/api/auth/signup', json={
            'email': 'testuser@example.com',
            'password': 'AnotherPassword123!'
        })
        assert response2.status_code == 409


class TestLogin:
    """Test user login endpoint."""
    
    def test_login_success(self, client, authenticated_user):
        """Test successful login with valid credentials."""
        response = client.post('/api/auth/login', json={
            'email': authenticated_user.email,
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 200
        data = response.get_json()
        
        assert 'access_token' in data
        assert 'refresh_token' in data
        assert data['user']['id'] == authenticated_user.id
        assert data['user']['email'] == authenticated_user.email
    
    def test_login_missing_email(self, client):
        """Test login fails without email."""
        response = client.post('/api/auth/login', json={
            'password': 'SomePassword123!'
        })
        
        assert response.status_code == 400
        assert 'Email and password required' in response.get_json()['error']
    
    def test_login_missing_password(self, client):
        """Test login fails without password."""
        response = client.post('/api/auth/login', json={
            'email': 'test@example.com'
        })
        
        assert response.status_code == 400
        assert 'Email and password required' in response.get_json()['error']
    
    def test_login_user_not_found(self, client):
        """Test login fails with non-existent email."""
        response = client.post('/api/auth/login', json={
            'email': 'nonexistent@example.com',
            'password': 'SomePassword123!'
        })
        
        assert response.status_code == 401
        assert 'Invalid email or password' in response.get_json()['error']
    
    def test_login_invalid_password(self, client, authenticated_user):
        """Test login fails with incorrect password."""
        response = client.post('/api/auth/login', json={
            'email': authenticated_user.email,
            'password': 'WrongPassword123!'
        })
        
        assert response.status_code == 401
        assert 'Invalid email or password' in response.get_json()['error']
    
    def test_login_resets_failed_attempts(self, client, authenticated_user):
        """Test successful login resets failed attempt counter."""
        # Simulate failed login
        authenticated_user.failed_login_attempts = 3
        
        # Successful login
        response = client.post('/api/auth/login', json={
            'email': authenticated_user.email,
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 200
        
        # Check failed attempts were reset
        updated_user = User.query.get(authenticated_user.id)
        assert updated_user.failed_login_attempts == 0


class TestAccountLockout:
    """Test account lockout protection."""
    
    def test_login_increments_failed_attempts(self, client, authenticated_user):
        """Test failed login increments attempt counter."""
        for i in range(3):
            response = client.post('/api/auth/login', json={
                'email': authenticated_user.email,
                'password': 'WrongPassword123!'
            })
            assert response.status_code == 401
        
        # Check failed attempts
        updated_user = User.query.get(authenticated_user.id)
        assert updated_user.failed_login_attempts == 3
    
    def test_login_locks_account_after_5_attempts(self, client, authenticated_user):
        """Test account locks after 5 failed login attempts."""
        # Simulate 5 failed attempts
        for i in range(5):
            response = client.post('/api/auth/login', json={
                'email': authenticated_user.email,
                'password': 'WrongPassword123!'
            })
            assert response.status_code == 401
        
        # Check account is locked
        updated_user = User.query.get(authenticated_user.id)
        assert updated_user.failed_login_attempts == 5
        assert updated_user.locked_until is not None
    
    def test_locked_account_cannot_login(self, client, authenticated_user):
        """Test locked account rejects login even with correct password."""
        # Lock the account
        from datetime import datetime, timezone as tz
        authenticated_user.locked_until = datetime.now(tz.utc) + timedelta(minutes=15)
        
        response = client.post('/api/auth/login', json={
            'email': authenticated_user.email,
            'password': 'TestPassword123!'  # Correct password
        })
        
        assert response.status_code == 429
        assert 'Account temporarily locked' in response.get_json()['error']
    
    def test_account_unlocks_after_timeout(self, client, authenticated_user):
        """Test account unlocks after timeout period expires."""
        from datetime import datetime, timezone as tz
        from backend.core.models import db
        
        # Lock account in the past (already expired)
        authenticated_user.locked_until = datetime.now(tz.utc) - timedelta(minutes=1)
        db.session.commit()
        
        response = client.post('/api/auth/login', json={
            'email': authenticated_user.email,
            'password': 'TestPassword123!'
        })
        
        assert response.status_code == 200


class TestTokenRefresh:
    """Test token refresh endpoint."""
    
    def test_refresh_token_success(self, client, authenticated_user):
        """Test successful token refresh."""
        refresh_token = core_auth.create_jwt_token(
            authenticated_user.id,
            authenticated_user.email,
            token_type='refresh'
        )
        
        response = client.post('/api/auth/refresh', json={
            'refresh_token': refresh_token
        })
        
        assert response.status_code == 200
        data = response.get_json()
        assert 'access_token' in data
    
    def test_refresh_missing_token(self, client):
        """Test refresh fails without token."""
        response = client.post('/api/auth/refresh', json={})
        
        assert response.status_code == 400
        assert 'Refresh token required' in response.get_json()['error']
    
    def test_refresh_invalid_token(self, client):
        """Test refresh fails with invalid token."""
        response = client.post('/api/auth/refresh', json={
            'refresh_token': 'invalid-token-xyz'
        })
        
        assert response.status_code == 401
        assert 'Invalid or expired refresh token' in response.get_json()['error']


class TestTokenVerification:
    """Test token verification endpoint."""
    
    def test_verify_valid_token(self, client, auth_headers, authenticated_user):
        """Test verification of valid token."""
        response = client.get('/api/auth/verify', headers=auth_headers)
        
        assert response.status_code == 200
        data = response.get_json()
        assert data['user']['id'] == authenticated_user.id
        assert data['user']['email'] == authenticated_user.email
    
    def test_verify_missing_token(self, client):
        """Test verification fails without token."""
        response = client.get('/api/auth/verify')
        
        assert response.status_code == 401
        assert 'Missing authorization token' in response.get_json()['error']
    
    def test_verify_invalid_token(self, client):
        """Test verification fails with invalid token."""
        response = client.get(
            '/api/auth/verify',
            headers={'Authorization': 'Bearer invalid-token'}
        )
        
        assert response.status_code == 401
        assert 'Invalid or expired token' in response.get_json()['error']


class TestLogout:
    """Test logout endpoint."""
    
    def test_logout_success(self, client, auth_headers):
        """Test successful logout."""
        response = client.post('/api/auth/logout', headers=auth_headers)
        
        assert response.status_code == 200
        assert 'success' in response.get_json()['message'].lower()
    
    def test_logout_without_token(self, client):
        """Test logout fails without token."""
        response = client.post('/api/auth/logout')
        
        assert response.status_code == 401


class TestCompleteAuthFlow:
    """Test complete authentication flow."""
    
    def test_signup_login_verify_logout(self, client):
        """Test complete auth flow: signup → login → verify → logout."""
        # Signup
        signup_response = client.post('/api/auth/signup', json={
            'email': 'flow@example.com',
            'password': 'FlowTest123!'
        })
        assert signup_response.status_code == 201
        signup_data = signup_response.get_json()
        user_id = signup_data['user']['id']
        
        # Login
        login_response = client.post('/api/auth/login', json={
            'email': 'flow@example.com',
            'password': 'FlowTest123!'
        })
        assert login_response.status_code == 200
        login_data = login_response.get_json()
        token = login_data['access_token']
        
        # Verify
        verify_response = client.get(
            '/api/auth/verify',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert verify_response.status_code == 200
        assert verify_response.get_json()['user']['id'] == user_id
        
        # Logout
        logout_response = client.post(
            '/api/auth/logout',
            headers={'Authorization': f'Bearer {token}'}
        )
        assert logout_response.status_code == 200
