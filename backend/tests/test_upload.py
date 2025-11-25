import io
import pytest
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..')))

from backend.main import app
from backend.core import auth as core_auth

MOCK_USER_ID = 'testuser'
MOCK_EMAIL = 'test@example.com'


@pytest.fixture
def client():
    """Create a test client with auth mocking."""
    app.config['TESTING'] = True
    app.config['ENV'] = 'testing'
    app.config['RATELIMIT_ENABLED'] = False
    
    with app.test_client() as client:
        yield client


def get_valid_token(user_id=MOCK_USER_ID, email=MOCK_EMAIL):
    """Generate a valid JWT token for testing."""
    with app.app_context():
        return core_auth.create_jwt_token(user_id, email, token_type='access')


def get_auth_header(token):
    """Create authorization header with token."""
    return {'Authorization': f'Bearer {token}'}


# Test upload endpoint

def test_upload_file_success(client, monkeypatch):
    """Test successful file upload."""
    def mock_upload_file(file_stream, filename, content_type, user_id):
        return f"{user_id}/{filename}"
    
    # Patch where the function is USED, not where it's defined
    monkeypatch.setattr('backend.routes.upload_routes.supabase_upload_file', mock_upload_file)
    
    token = get_valid_token()
    data = {
        'file': (io.BytesIO(b"testdata"), 'test.jpg')
    }
    headers = get_auth_header(token)
    response = client.post('/api/upload', data=data, headers=headers, content_type='multipart/form-data')
    
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['file_key'] == f"{MOCK_USER_ID}/test.jpg"


def test_upload_file_missing(client):
    """Test upload without file."""
    token = get_valid_token()
    headers = get_auth_header(token)
    response = client.post('/api/upload', data={}, headers=headers)
    
    assert response.status_code == 400
    assert 'error' in response.json


def test_get_file_success(client, monkeypatch):
    """Test successful file download."""
    def mock_get_signed_url(file_key, expires_in=3600):
        return f"https://supabase.mock/{file_key}?token=abc"
    
    # Patch where the function is USED, not where it's defined
    monkeypatch.setattr('backend.routes.upload_routes.supabase_get_signed_url', mock_get_signed_url)
    
    token = get_valid_token()
    headers = get_auth_header(token)
    file_key = f"{MOCK_USER_ID}/test.jpg"
    response = client.get(f'/api/uploads/{file_key}', headers=headers)
    
    assert response.status_code == 200
    assert 'url' in response.json


def test_get_file_unauthorized(client):
    """Test download of file from different user."""
    token = get_valid_token(user_id='otheruser')
    headers = get_auth_header(token)
    file_key = f"{MOCK_USER_ID}/test.jpg"
    response = client.get(f'/api/uploads/{file_key}', headers=headers)
    
    assert response.status_code == 403
    assert 'error' in response.json

