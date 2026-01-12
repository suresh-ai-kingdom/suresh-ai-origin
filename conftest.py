import os
import sys
import pytest

# Ensure repo root is on sys.path so tests can import pp when pytest's cwd varies.
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture(autouse=True)
def isolate_session_config_tests(request, monkeypatch):
    '''Isolate session cookie config tests to prevent cross-test pollution.'''
    # Only apply to session cookie config tests
    if 'test_session_cookie' in request.node.nodeid:
        # Store original state before test
        original_httponly = app.config.get('SESSION_COOKIE_HTTPONLY')
        original_secure = app.config.get('SESSION_COOKIE_SECURE')
        original_samesite = app.config.get('SESSION_COOKIE_SAMESITE')
        
        yield
        
        # Restore original state after test
        app.config['SESSION_COOKIE_HTTPONLY'] = original_httponly
        app.config['SESSION_COOKIE_SECURE'] = original_secure
        app.config['SESSION_COOKIE_SAMESITE'] = original_samesite
    else:
        yield
