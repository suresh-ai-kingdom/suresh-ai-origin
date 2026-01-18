"""
Comprehensive tests for observability, webhooks, and provider adapters.

Run with:
    pytest tests/test_analytics_integrations.py -v
"""

from __future__ import annotations

import json
import tempfile
import os
from pathlib import Path


def test_observability_safe_len():
    """Test _safe_len handles various object types."""
    from observability import _safe_len

    assert _safe_len(b"hello") == 5
    assert _safe_len({"key": "value"}) > 0
    assert _safe_len(None) >= 0


def test_observability_log_event():
    """Test log_event writes to JSONL file."""
    from observability import log_event, _EVENT_FILE

    # Temporarily override event file
    original_file = _EVENT_FILE
    with tempfile.TemporaryDirectory() as tmpdir:
        event_file = os.path.join(tmpdir, "test_events.jsonl")
        import observability
        observability._EVENT_FILE = event_file

        try:
            log_event({"test": "event", "ts": 1000})
            assert os.path.exists(event_file), "Event file not created"
            with open(event_file, "r") as f:
                lines = f.readlines()
            assert len(lines) == 1
            parsed = json.loads(lines[0])
            assert parsed["test"] == "event"
        finally:
            observability._EVENT_FILE = original_file


def test_webhooks_blueprint_make():
    """Test Make.com webhook endpoint (mocked Flask)."""
    from integrations.no_code_webhooks import bp

    # Create a minimal Flask app for testing
    from flask import Flask
    app = Flask(__name__)
    app.register_blueprint(bp)

    with app.test_client() as client:
        # Valid request
        response = client.post(
            "/hooks/make",
            json={"test": "data"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


def test_webhooks_blueprint_zapier():
    """Test Zapier webhook endpoint (mocked Flask)."""
    from integrations.no_code_webhooks import bp
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(bp)

    with app.test_client() as client:
        response = client.post(
            "/hooks/zapier",
            json={"test": "zapier_data"},
            content_type="application/json",
        )
        assert response.status_code == 200
        data = response.get_json()
        assert data["success"] is True


def test_webhooks_secret_validation():
    """Test webhook secret verification."""
    from integrations.no_code_webhooks import bp, _verify_secret
    from flask import Flask

    app = Flask(__name__)
    app.register_blueprint(bp)

    # Set a secret
    os.environ["WEBHOOK_SHARED_SECRET"] = "test_secret_123"

    with app.test_client() as client:
        # Request without secret should fail
        response = client.post(
            "/hooks/make",
            json={"test": "data"},
            content_type="application/json",
        )
        assert response.status_code == 403

        # Request with correct secret should pass
        response = client.post(
            "/hooks/make",
            json={"test": "data"},
            headers={"X-Webhook-Secret": "test_secret_123"},
            content_type="application/json",
        )
        assert response.status_code == 200


def test_claude_provider_init():
    """Test ClaudeProvider initialization."""
    from integrations.providers import ClaudeProvider

    # Without API key (should log warning but not crash)
    provider = ClaudeProvider(api_key="sk_test_123")
    assert provider.api_key == "sk_test_123"
    assert provider.model == "claude-3-5-sonnet-20241022"

    # With custom model
    provider2 = ClaudeProvider(api_key="sk_test_456", model="claude-3-opus-20240229")
    assert provider2.model == "claude-3-opus-20240229"


def test_openai_provider_init():
    """Test OpenAIProvider initialization."""
    from integrations.providers import OpenAIProvider

    provider = OpenAIProvider(api_key="sk_test_789")
    assert provider.api_key == "sk_test_789"
    assert provider.model == "gpt-4o-mini"

    provider2 = OpenAIProvider(api_key="sk_test_999", model="gpt-4-turbo")
    assert provider2.model == "gpt-4-turbo"


def test_providers_abstract_interface():
    """Test that providers inherit from AIProvider and have invoke."""
    from integrations.providers import AIProvider, ClaudeProvider, OpenAIProvider

    for Provider in [ClaudeProvider, OpenAIProvider]:
        provider = Provider(api_key="test_key")
        assert isinstance(provider, AIProvider)
        assert hasattr(provider, "invoke")
        assert callable(provider.invoke)
