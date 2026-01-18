"""
Basic API tests for rare features endpoints.
Uses monkeypatch to stub AI outputs to avoid external calls.
Run with: pytest -q
"""

from typing import Dict
import json

def _fake_generate_ai_content(prompt: str, **kwargs) -> str:
    return f"FAKE_AI_OUTPUT for prompt length={len(prompt)}"


def test_destiny_blueprint(client, monkeypatch):
    from rare_1_percent_features import generate_destiny_blueprint
    monkeypatch.setattr(
        "real_ai_service.generate_ai_content",
        _fake_generate_ai_content,
        raising=True,
    )
    payload = {
        "business_name": "TestCo",
        "current_revenue": 100000,
        "target_revenue": 10000000,
        "industry": "SaaS",
    }
    result = generate_destiny_blueprint(payload)
    assert result["success"] is True
    assert "destiny_blueprint" in result


def test_perfect_timing_variants(monkeypatch):
    from rare_1_percent_features import calculate_perfect_timing
    monkeypatch.setattr(
        "real_ai_service.generate_ai_content",
        _fake_generate_ai_content,
        raising=True,
    )
    # list of dicts
    r1 = calculate_perfect_timing([
        {"decision": "Launch PH", "context": "MVP ready"},
        {"decision": "Hire SDR", "context": "Pipeline active"},
    ])
    assert r1["success"] is True

    # single dict
    r2 = calculate_perfect_timing({"decision": "Increase pricing", "context": "High demand"})
    assert r2["success"] is True

    # list of strings
    r3 = calculate_perfect_timing(["Run campaign", "Start podcast"])
    assert r3["success"] is True

    # single string
    r4 = calculate_perfect_timing("Expand to Singapore")
    assert r4["success"] is True


def test_market_consciousness(monkeypatch):
    from rare_1_percent_features import predict_market_future
    monkeypatch.setattr(
        "real_ai_service.generate_ai_content",
        _fake_generate_ai_content,
        raising=True,
    )
    result = predict_market_future({"market": "AI Automation"})
    assert result["success"] is True


def test_customer_soul(monkeypatch):
    from rare_1_percent_features import map_customer_soul
    monkeypatch.setattr(
        "real_ai_service.generate_ai_content",
        _fake_generate_ai_content,
        raising=True,
    )
    result = map_customer_soul({"product": "Automation", "behavior": "Research"})
    assert result["success"] is True
