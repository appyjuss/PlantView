import io
import pytest
from backend.main import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def get_auth_header(token):
    return {'Authorization': f'Bearer {token}'}

# Mock JWT token for testing (replace with real token logic if needed)
MOCK_TOKEN = 'test.jwt.token'
MOCK_USER_ID = 'testuser'

# Test upload endpoint

def test_upload_file_success(client, monkeypatch):
    def mock_upload_file(file_stream, filename, content_type, user_id):
        return f"{user_id}/{filename}"
    monkeypatch.setattr('backend.core.storage.supabase_upload_file', mock_upload_file)
    data = {
        'file': (io.BytesIO(b"testdata"), 'test.jpg')
    }
    headers = get_auth_header(MOCK_TOKEN)
    response = client.post('/API/upload', data=data, headers=headers, content_type='multipart/form-data')
    assert response.status_code == 201
    assert response.json['success'] is True
    assert response.json['file_key'] == f"{MOCK_USER_ID}/test.jpg"

# Test upload endpoint with missing file

def test_upload_file_missing(client):
    headers = get_auth_header(MOCK_TOKEN)
    response = client.post('/API/upload', data={}, headers=headers)
    assert response.status_code == 400
    assert 'error' in response.json

# Test download endpoint

def test_get_file_success(client, monkeypatch):
    def mock_get_signed_url(file_key, expires_in=3600):
        return f"https://supabase.mock/{file_key}?token=abc"
    monkeypatch.setattr('backend.core.storage.supabase_get_signed_url', mock_get_signed_url)
    headers = get_auth_header(MOCK_TOKEN)
    file_key = f"{MOCK_USER_ID}/test.jpg"
    response = client.get(f'/API/uploads/{file_key}', headers=headers)
    assert response.status_code == 200
    assert 'url' in response.json

# Test download endpoint unauthorized

def test_get_file_unauthorized(client):
    headers = get_auth_header(MOCK_TOKEN)
    file_key = "otheruser/test.jpg"
    response = client.get(f'/API/uploads/{file_key}', headers=headers)
    assert response.status_code == 403
    assert 'error' in response.json
