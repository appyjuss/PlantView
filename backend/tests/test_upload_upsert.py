import io
from backend.core import storage


def _make_response(status_code, text=None, json_obj=None):
    class Resp:
        def __init__(self):
            self.status_code = status_code
            self.text = text or ''

        def json(self):
            return json_obj

    return Resp()


def test_upload_success(client, auth_headers, monkeypatch):
    # Ensure SUPABASE env exists for storage to proceed
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'testkey')

    # Mock requests.post to return 201
    def fake_post(url, headers=None, data=None, timeout=None):
        return _make_response(201, text='ok', json_obj={'ok': True})

    monkeypatch.setattr('backend.core.storage.requests.post', fake_post)

    data = {'file': (io.BytesIO(b'hello'), 'test.jpg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 201
    j = resp.get_json()
    assert j and j.get('success') is True


def test_upload_upsert_treated_as_success_when_enabled(client, auth_headers, monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'testkey')
    monkeypatch.setenv('SUPABASE_UPSERT', 'true')

    def fake_post(url, headers=None, data=None, timeout=None):
        return _make_response(409, text='{"statusCode":409,"error":"Duplicate"}', json_obj={'statusCode': 409})

    monkeypatch.setattr('backend.core.storage.requests.post', fake_post)

    data = {'file': (io.BytesIO(b'hello'), 'test.jpg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 201
    j = resp.get_json()
    assert j and j.get('success') is True


def test_upload_upsert_disabled_returns_500_on_duplicate(client, auth_headers, monkeypatch):
    monkeypatch.setenv('SUPABASE_URL', 'https://example.supabase.co')
    monkeypatch.setenv('SUPABASE_SERVICE_ROLE_KEY', 'testkey')
    monkeypatch.setenv('SUPABASE_UPSERT', 'false')

    def fake_post(url, headers=None, data=None, timeout=None):
        return _make_response(409, text='{"statusCode":409,"error":"Duplicate"}', json_obj={'statusCode': 409})

    monkeypatch.setattr('backend.core.storage.requests.post', fake_post)

    data = {'file': (io.BytesIO(b'hello'), 'test.jpg')}
    resp = client.post('/api/upload', data=data, headers=auth_headers, content_type='multipart/form-data')
    assert resp.status_code == 500
