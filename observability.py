"""
Observability and lightweight analytics for API usage.

Logs each API call to a JSONL file `data/api_events.jsonl` with:
- timestamp, request_id, path, method, feature_name, status_code, duration_ms, bytes_in, bytes_out

Usage:
    from observability import track_api_usage
    
    @app.route('/api/rare/destiny', methods=['POST'])
    @track_api_usage('rare_destiny')
    def destiny():
        ...

This avoids DB migrations by using append-only JSONL. It is safe for Render.
"""

from __future__ import annotations

import os
import time
import json
import logging
from typing import Any, Callable, Optional

from flask import request

logger = logging.getLogger(__name__)

_EVENT_DIR = os.path.join(os.getcwd(), "data")
_EVENT_FILE = os.path.join(_EVENT_DIR, "api_events.jsonl")


def _ensure_event_file() -> None:
    try:
        os.makedirs(_EVENT_DIR, exist_ok=True)
        if not os.path.exists(_EVENT_FILE):
            with open(_EVENT_FILE, "a", encoding="utf-8") as f:
                f.write("")
    except Exception as e:
        logger.warning("Observability: Could not prepare event file: %s", e)


def _safe_len(obj: Any) -> int:
    try:
        if isinstance(obj, (bytes, bytearray)):
            return len(obj)
        s = json.dumps(obj, ensure_ascii=False)
        return len(s.encode("utf-8"))
    except Exception:
        return 0


def log_event(event: dict) -> None:
    """Append a single event to JSONL file."""
    _ensure_event_file()
    try:
        with open(_EVENT_FILE, "a", encoding="utf-8") as f:
            f.write(json.dumps(event, ensure_ascii=False) + "\n")
    except Exception as e:
        logger.warning("Observability: Failed to log event: %s", e)


def track_api_usage(feature_name: Optional[str] = None) -> Callable:
    """Flask-compatible decorator to log API usage and latency.

    Wrap after `@app.route` and before the handler function.
    """

    def decorator(fn: Callable) -> Callable:
        def wrapper(*args, **kwargs):
            start = time.time()
            rid = getattr(request, "headers", {}).get("X-Request-ID")
            try:
                bytes_in = _safe_len(getattr(request, "data", b"")) or _safe_len(getattr(request, "json", {}))
            except Exception:
                bytes_in = 0

            try:
                resp = fn(*args, **kwargs)
                # Flask handlers may return tuple (body, status)
                status_code = 200
                body = resp
                if isinstance(resp, tuple) and len(resp) >= 2:
                    body, status_code = resp[0], resp[1]
                duration_ms = int((time.time() - start) * 1000)
                event = {
                    "ts": int(time.time() * 1000),
                    "request_id": rid,
                    "path": request.path,
                    "method": request.method,
                    "feature": feature_name,
                    "status": status_code,
                    "duration_ms": duration_ms,
                    "bytes_in": bytes_in,
                    "bytes_out": _safe_len(body),
                }
                log_event(event)
                return resp
            except Exception as e:
                duration_ms = int((time.time() - start) * 1000)
                event = {
                    "ts": int(time.time() * 1000),
                    "request_id": rid,
                    "path": request.path,
                    "method": request.method,
                    "feature": feature_name,
                    "status": 500,
                    "duration_ms": duration_ms,
                    "bytes_in": bytes_in,
                    "error": str(e),
                }
                log_event(event)
                raise

        # Preserve name for Flask
        wrapper.__name__ = getattr(fn, "__name__", "wrapped_fn")
        wrapper.__doc__ = fn.__doc__
        return wrapper

    return decorator
