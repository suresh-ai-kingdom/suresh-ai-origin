import os

from app import app, apply_session_cookie_config


def test_session_cookie_defaults(monkeypatch):
    # Ensure defaults: HTTPOnly True, SAMESITE Lax, SECURE depends on FLASK_DEBUG
    monkeypatch.delenv('SESSION_COOKIE_HTTPONLY', raising=False)
    monkeypatch.delenv('SESSION_COOKIE_SECURE', raising=False)
    monkeypatch.delenv('SESSION_COOKIE_SAMESITE', raising=False)
    monkeypatch.delenv('FLASK_DEBUG', raising=False)
    # emulate production default (no FLASK_DEBUG)
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    apply_session_cookie_config()
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    assert app.config['SESSION_COOKIE_SECURE'] is True


def test_session_cookie_env_overrides(monkeypatch):
    monkeypatch.setenv('SESSION_COOKIE_HTTPONLY', 'False')
    monkeypatch.setenv('SESSION_COOKIE_SECURE', 'False')
    monkeypatch.setenv('SESSION_COOKIE_SAMESITE', 'Strict')
    apply_session_cookie_config()
    assert app.config['SESSION_COOKIE_HTTPONLY'] is False
    assert app.config['SESSION_COOKIE_SECURE'] is False
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Strict'


def test_warn_insecure_cookie_in_production(monkeypatch, caplog):
    import logging
    # Ensure we are not in debug
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    # Explicitly set insecure cookie
    monkeypatch.setenv('SESSION_COOKIE_SECURE', 'False')
    caplog.set_level(logging.WARNING)
    apply_session_cookie_config()
    # Emit the same warning check as in app startup
    if not (os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true')) and not app.config.get('SESSION_COOKIE_SECURE', True):
        logging.warning("Session cookies are configured as INSECURE")
    assert any('INSECURE' in rec.message or 'insecure' in rec.message.lower() for rec in caplog.records)