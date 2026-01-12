"""AI Chatbot engine with safe fallback.

- If Claude/Anthropic keys are present, you can integrate; for tests we use rule-based responses.
- Deterministic, offline-friendly behavior.
"""
import os
import time
from datetime import datetime
from typing import List, Dict, Optional

# Simple intents and canned responses (fallback)
INTENTS = {
    "hello": "Hello! 👋 How can I help you today?",
    "pricing": "Our packs: Starter ₹99, Pro ₹499, Premium ₹999, Platinum ₹2999.",
    "refund": "Refunds are handled within 5-7 days. Please share your receipt.",
    "download": "You can download from the Success page or the Downloads section.",
    "support": "You can reach support at support@example.com or chat here 24/7.",
}

SUGGESTIONS = [
    {"label": "View Pricing", "action": "open:/buy"},
    {"label": "My Downloads", "action": "open:/success"},
    {"label": "Contact Support", "action": "open:/admin"},
]


def detect_intent(message: str) -> Optional[str]:
    m = (message or "").lower()
    if any(word in m for word in ["hi", "hello", "hey", "namaste"]):
        return "hello"
    if any(word in m for word in ["price", "pricing", "cost"]):
        return "pricing"
    if "refund" in m:
        return "refund"
    if any(word in m for word in ["download", "link"]):
        return "download"
    if any(word in m for word in ["help", "support"]):
        return "support"
    return None


def _fallback_reply(message: str) -> Dict:
    intent = detect_intent(message)
    if intent and intent in INTENTS:
        reply = INTENTS[intent]
    else:
        reply = (
            "Thanks for your message! I can help with pricing, downloads, refunds, and support. "
            "Try asking: 'What is the price?' or 'I need help with my order'."
        )
    return {
        "type": "text",
        "content": reply,
        "intent": intent or "general",
        "suggestions": SUGGESTIONS,
    }


def chat_reply(message: str, history: Optional[List[Dict]] = None, customer_receipt: Optional[str] = None) -> Dict:
    """Generate a chatbot reply.

    Args:
        message: User message text
        history: Previous turns, list of {role, content}
        customer_receipt: Optional receipt to personalize

    Returns dict {success, reply: {...}, meta: {...}}
    """
    start = time.time()

    # Offline-safe fallback
    reply_obj = _fallback_reply(message)

    meta = {
        "receipt": customer_receipt,
        "timestamp": datetime.now().isoformat(),
        "latency_ms": int((time.time() - start) * 1000),
    }
    return {"success": True, "reply": reply_obj, "meta": meta}
