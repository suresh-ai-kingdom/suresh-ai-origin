import os
import time
import logging
import threading
import hmac
import hashlib
from collections import deque

# Feature names: 'download', 'attribution_run', 'export', 'history', 'create_order'
# Env flags to avoid breaking existing tests; enable in production.
ENFORCE_ENTITLEMENTS = os.getenv('ENFORCE_ENTITLEMENTS', 'False').lower() in ('1', 'true', 'yes')
ENFORCE_IDEMPOTENCY = os.getenv('ENFORCE_IDEMPOTENCY', 'False').lower() in ('1', 'true', 'yes')
DOWNLOAD_TOKEN_TTL = int(os.getenv('DOWNLOAD_TOKEN_TTL', '900'))  # seconds
BIND_DOWNLOAD_TOKEN_TO_IP = os.getenv('BIND_DOWNLOAD_TOKEN_TO_IP', 'False').lower() in ('1', 'true', 'yes')

# Simple token buckets per feature+key (IP/user) with runtime-configurable limits
_RATE_LOCK = threading.Lock()
_RATE_BUCKETS: dict[str, deque] = {}


def _rate_key(feature: str, ip: str | None) -> str:
    return f"{feature}:{ip or 'unknown'}"


def _get_limit_window(feature: str) -> tuple[int, int]:
    # Default limits per feature; override via ENV: RATE_<FEATURE>_LIMIT, RATE_<FEATURE>_WINDOW
    defaults = {
        'download': (30, 60),        # 30 req/min per IP
        'create_order': (10, 60),    # 10 req/min per IP
        'export': (15, 60),
        'attribution_run': (120, 60),
    }
    limit, window = defaults.get(feature, (60, 60))
    limit = int(os.getenv(f"RATE_{feature.upper()}_LIMIT", limit))
    window = int(os.getenv(f"RATE_{feature.upper()}_WINDOW", window))
    return limit, window


def rate_limit_feature(feature: str):
    """Decorator to enforce per-IP rate limits before any work.
    Returns 429 with Retry-After when exceeded. Lightweight and in-memory.
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                from flask import request, jsonify
                ip = request.remote_addr
                now = time.time()
                limit, window = _get_limit_window(feature)
                key = _rate_key(feature, ip)
                with _RATE_LOCK:
                    q = _RATE_BUCKETS.get(key)
                    if q is None:
                        q = deque()
                        _RATE_BUCKETS[key] = q
                    # expire old entries
                    while q and q[0] <= now - window:
                        q.popleft()
                    if len(q) >= limit:
                        retry_after = int(window - (now - q[0])) if q else window
                        logging.warning("rate_limit hit: feature=%s ip=%s limit=%s window=%s", feature, ip, limit, window)
                        resp = jsonify({'error': 'rate_limited', 'feature': feature, 'retry_after': retry_after})
                        return (resp, 429, {'Retry-After': str(retry_after)})
                    q.append(now)
            except Exception:
                # Fail closed? For rate limiting we prefer allow on internal error to avoid DOS.
                pass
            return func(*args, **kwargs)
        # Preserve Flask route metadata
        wrapper.__name__ = getattr(func, '__name__', f"{feature}_rate_limited")
        return wrapper
    return decorator


def check_entitlement(feature: str, context: dict | None = None) -> dict:
    """Centralized entitlement decision.
    Returns dict with: allow: bool, reason: str, upgrade_url: str | None, usage: dict
    """
    context = context or {}
    # Snapshot usage (read-only; can be wired to real counters)
    try:
        from app import get_current_plan, get_plan_limits, get_plan_usage_snapshot
        plan = get_current_plan()
        limits = get_plan_limits(plan)
        usage = get_plan_usage_snapshot()
    except Exception:
        plan, limits, usage = 'pro', {}, {}

    allow = True
    reason = 'allowed'
    upgrade_url = '/buy?product=pro'

    # Emit usage threshold alerts (80/90/100/110) for attribution
    try:
        cap_thr = limits.get('attribution_runs', 0)
        used_thr = usage.get('attribution_runs', 0)
        pct = int((used_thr / cap_thr) * 100) if cap_thr else 0
        if pct >= 110:
            emit_alert('usage_hard_block', {'feature': 'attribution_run', 'used': used_thr, 'cap': cap_thr, 'pct': pct})
        elif pct >= 100:
            emit_alert('usage_grace', {'feature': 'attribution_run', 'used': used_thr, 'cap': cap_thr, 'pct': pct})
        elif pct >= 90:
            emit_alert('usage_90', {'feature': 'attribution_run', 'used': used_thr, 'cap': cap_thr, 'pct': pct})
        elif pct >= 80:
            emit_alert('usage_80', {'feature': 'attribution_run', 'used': used_thr, 'cap': cap_thr, 'pct': pct})
    except Exception:
        pass

    if ENFORCE_ENTITLEMENTS:
        if feature == 'download':
            product = context.get('product')
            # Free product is always allowed; premium require entitlement
            free_products = {'starter'}
            if product not in free_products:
                # Require signed token for premium downloads
                token = context.get('token')
                ip = context.get('ip')
                bind_ip = ip if BIND_DOWNLOAD_TOKEN_TO_IP else None
                if not token or not verify_download_token(token, product, bind_ip):
                    allow = False
                    reason = f'premium_download_requires_token:{product}'
                    upgrade_url = f"/buy?product={product}"
                else:
                    reason = 'allowed_with_token'
        elif feature == 'export':
            if not limits.get('export'):
                allow = False
                reason = 'export_not_in_plan'
        elif feature == 'attribution_run':
            cap = limits.get('attribution_runs', 0)
            used = usage.get('attribution_runs', 0)
            grace_pct = int(os.getenv('PLAN_ATTRIBUTION_GRACE_PERCENT', '10'))  # allow up to +10%
            hard_cap = int(cap * (1 + (grace_pct / 100))) if cap else 0
            if cap and used >= hard_cap:
                allow = False
                reason = 'attribution_hard_block_110pct'
                upgrade_url = '/buy?product=scale'
            elif cap and used >= cap:
                # Grace window (soft allow)
                allow = True
                reason = 'attribution_grace_window'
                upgrade_url = '/buy?product=scale'
        # Other features can be added here

    log_entitlement_decision(feature, plan, limits, usage, allow, reason, context)
    return {
        'allow': allow,
        'reason': reason,
        'upgrade_url': upgrade_url,
        'usage': usage,
        'plan': plan,
    }


def log_entitlement_decision(feature: str, plan: str, limits: dict, usage: dict, allow: bool, reason: str, context: dict):
    logging.info(
        "entitlement_decision: feature=%s plan=%s allow=%s reason=%s limits=%s usage=%s context=%s",
        feature, plan, allow, reason, limits, usage, context
    )
    # Emit alerts on deny or hard blocks
    try:
        if not allow or 'hard_block' in reason:
            emit_alert('entitlement_denied', {'feature': feature, 'plan': plan, 'reason': reason})
    except Exception:
        pass


def require_idempotency_key(func):
    """Decorator to require Idempotency-Key for POST requests when enabled.
    Returns 400 if missing; logs key usage for audit. Does not persist keys yet.
    """
    def wrapper(*args, **kwargs):
        try:
            from flask import request, jsonify
            if request.method == 'POST' and ENFORCE_IDEMPOTENCY:
                key = request.headers.get('Idempotency-Key')
                if not key:
                    logging.warning('idempotency_missing for %s', request.path)
                    return jsonify({'error': 'idempotency_key_required'}), 400
                logging.info('idempotency_key: path=%s key=%s', request.path, key)
        except Exception:
            pass
        return func(*args, **kwargs)
    wrapper.__name__ = getattr(func, '__name__', 'require_idempotency_key_wrapped')
    return wrapper


def _hmac_payload(secret: str, payload: str) -> str:
    return hmac.new(secret.encode(), payload.encode(), hashlib.sha256).hexdigest()


def generate_download_token(product: str, ip: str | None = None, ttl: int | None = None) -> str:
    """Create a signed token for premium downloads with expiry.
    Format: expires_epoch.hmac(product|expires|ip?)
    """
    try:
        from flask import current_app
        secret = current_app.config.get('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY', 'dev-secret')
    except Exception:
        secret = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
    ttl = ttl if ttl is not None else DOWNLOAD_TOKEN_TTL
    expires = int(time.time()) + max(1, ttl)
    base = f"{product}|{expires}"
    if ip:
        base = base + f"|{ip}"
    signature = _hmac_payload(secret, base)
    return f"{expires}.{signature}"


def verify_download_token(token: str, product: str, ip: str | None = None) -> bool:
    """Verify signed download token.
    Returns True if valid and not expired.
    """
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return False
        expires = int(parts[0])
        sig = parts[1]
        if expires < int(time.time()):
            return False
        try:
            from flask import current_app
            secret = current_app.config.get('SECRET_KEY') or os.getenv('FLASK_SECRET_KEY', 'dev-secret')
        except Exception:
            secret = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
        base = f"{product}|{expires}"
        if ip:
            base = base + f"|{ip}"
        expected = _hmac_payload(secret, base)
        return hmac.compare_digest(expected, sig)
    except Exception:
        return False


def emit_alert(event: str, data: dict):
    """Emit alert as structured log; placeholder for external alerting.
    """
    logging.warning("ALERT %s %s", event, data)
