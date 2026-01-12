import os
import sys
import pytest

# Ensure repo root is on sys.path so tests can import app when pytest's cwd varies.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app, apply_session_cookie_config

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(scope='function')
def reset_session_config(monkeypatch):
    """Reset session cookie config to defaults before session cookie tests."""
    # Clear all session cookie env vars
    monkeypatch.delenv('SESSION_COOKIE_HTTPONLY', raising=False)
    monkeypatch.delenv('SESSION_COOKIE_SECURE', raising=False)
    monkeypatch.delenv('SESSION_COOKIE_SAMESITE', raising=False)
    monkeypatch.delenv('FLASK_DEBUG', raising=False)
    # Re-apply default config
    apply_session_cookie_config()
    yield
