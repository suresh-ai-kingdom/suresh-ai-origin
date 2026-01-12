"""Tests for AI Chatbot fallback behavior."""
import os
import sys
import pytest

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from chatbot import chat_reply, detect_intent


def test_detect_intent_basic():
    assert detect_intent("hello there") == "hello"
    assert detect_intent("what's the pricing?") == "pricing"
    assert detect_intent("I need a refund") == "refund"
    assert detect_intent("how to download") == "download"
    assert detect_intent("support please") == "support"


def test_chat_reply_fallback_general():
    res = chat_reply("random question about stars")
    assert res["success"] is True
    assert "reply" in res
    assert res["reply"]["type"] == "text"
    assert isinstance(res["reply"]["content"], str)
    assert res["reply"]["intent"] == "general"
    assert isinstance(res["reply"]["suggestions"], list)


def test_chat_reply_pricing():
    res = chat_reply("price of pro pack?")
    assert res["reply"]["intent"] == "pricing"
    assert "₹" in res["reply"]["content"]


def test_chat_reply_latency_and_meta():
    res = chat_reply("hello")
    meta = res.get("meta", {})
    assert "timestamp" in meta
    assert "latency_ms" in meta
    assert isinstance(meta["latency_ms"], int)
