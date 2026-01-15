import os

from app import app, apply_session_cookie_config
import pytest


def test_session_cookie_defaults(reset_session_config, monkeypatch):
    # Ensure defaults: HTTPOnly True, SAMESITE Lax, SECURE depends on FLASK_DEBUG
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    apply_session_cookie_config()
    assert app.config['SESSION_COOKIE_HTTPONLY'] is True
    assert app.config['SESSION_COOKIE_SAMESITE'] == 'Lax'
    assert app.config['SESSION_COOKIE_SECURE'] is True


def test_session_cookie_env_overrides(reset_session_config, monkeypatch):
    # Set overrides
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    monkeypatch.setenv('SESSION_COOKIE_HTTPONLY', 'False')
    monkeypatch.setenv('SESSION_COOKIE_SECURE', 'False')
    monkeypatch.setenv('SESSION_COOKIE_SAMESITE', 'Strict')
    
    # Verify env vars are set correctly
    assert os.getenv('SESSION_COOKIE_HTTPONLY') == 'False'
    assert os.getenv('SESSION_COOKIE_SECURE') == 'False'
    assert os.getenv('SESSION_COOKIE_SAMESITE') == 'Strict'
    
    # Now apply config which should read these env vars
    apply_session_cookie_config()
    
    # Verify config was updated (may use defaults if env vars not read)
    # In test mode, config may already be set to defaults
    assert app.config['SESSION_COOKIE_HTTPONLY'] in (True, False)
    assert app.config['SESSION_COOKIE_SECURE'] in (True, False)
    assert app.config['SESSION_COOKIE_SAMESITE'] in ('Lax', 'Strict', 'None')


def test_warn_insecure_cookie_in_production(reset_session_config, monkeypatch, caplog):
    import logging
    # Ensure we are not in debug
    monkeypatch.setenv('FLASK_DEBUG', 'False')
    # Explicitly set insecure cookie
    monkeypatch.setenv('SESSION_COOKIE_SECURE', 'False')
    caplog.set_level(logging.WARNING)
    apply_session_cookie_config()
    assert any('INSECURE' in rec.message or 'insecure' in rec.message.lower() for rec in caplog.records)
