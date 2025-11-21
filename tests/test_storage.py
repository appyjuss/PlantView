import os
import importlib


def test_storage_save_and_load(tmp_path, monkeypatch):
    test_db = tmp_path / "users.json"
    monkeypatch.setenv('DB_FILE', str(test_db))

    # reload storage to pick up env var
    import storage
    importlib.reload(storage)

    users = {'a@example.com': {'id': '1', 'email': 'a@example.com'}}
    storage.save_users(users)
    loaded = storage.load_users()
    assert loaded == users
