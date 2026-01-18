"""
No-code webhook integrations for Make.com and Zapier.

Provides a Flask Blueprint with `/hooks/make` and `/hooks/zapier`.
Validates an optional shared secret in header `X-Webhook-Secret`.
Logs incoming payloads to `data/webhooks.jsonl` for later processing.
"""

from __future__ import annotations

import os
import json
import time
import logging
from typing import Dict, Any

from flask import Blueprint, request, jsonify

logger = logging.getLogger(__name__)

bp = Blueprint("no_code_webhooks", __name__)

_DIR = os.path.join(os.getcwd(), "data")
_FILE = os.path.join(_DIR, "webhooks.jsonl")


def _append(payload: Dict[str, Any]) -> None:
    os.makedirs(_DIR, exist_ok=True)
    with open(_FILE, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")


def _verify_secret() -> bool:
    secret = os.getenv("WEBHOOK_SHARED_SECRET", "")
    incoming = request.headers.get("X-Webhook-Secret", "")
    return not secret or secret == incoming


@bp.route("/hooks/make", methods=["POST"])
def hooks_make():
    if not _verify_secret():
        return jsonify({"success": False, "error": "invalid_secret"}), 403
    payload = {
        "ts": int(time.time() * 1000),
        "source": "make.com",
        "headers": dict(request.headers),
        "json": request.json,
    }
    _append(payload)
    return jsonify({"success": True}), 200


@bp.route("/hooks/zapier", methods=["POST"])
def hooks_zapier():
    if not _verify_secret():
        return jsonify({"success": False, "error": "invalid_secret"}), 403
    payload = {
        "ts": int(time.time() * 1000),
        "source": "zapier",
        "headers": dict(request.headers),
        "json": request.json,
    }
    _append(payload)
    return jsonify({"success": True}), 200
