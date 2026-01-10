from flask import Flask, render_template, send_from_directory, request, jsonify, redirect, url_for, session, flash, abort
import os
import logging
import time
import functools
from dotenv import load_dotenv
import razorpay
from werkzeug.security import check_password_hash
import secrets
import threading
from collections import deque

# Load .env when present (development convenience). In production, the host/CI should set env vars.
load_dotenv()

app = Flask(__name__)
# Ensure a Flask secret key is configured; use FLASK_SECRET_KEY in production
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'dev-secret')
logging.basicConfig(level=logging.INFO)


def apply_session_cookie_config():
    """Apply session cookie configuration from environment variables.

    - SESSION_COOKIE_HTTPONLY: 'True'/'False' (default True)
    - SESSION_COOKIE_SECURE: 'True'/'False' (default True when not in debug)
    - SESSION_COOKIE_SAMESITE: 'Lax'|'Strict'|'None' (default 'Lax')

    Call this after changing env vars in tests or at startup.
    """
    # HttpOnly defaults to True
    http_only = os.getenv('SESSION_COOKIE_HTTPONLY', 'True').lower() in ('1', 'true', 'yes')
    # Secure defaults to True unless FLASK_DEBUG is true
    flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true')
    default_secure = not flask_debug
    secure = os.getenv('SESSION_COOKIE_SECURE')
    if secure is None:
        secure_flag = default_secure
    else:
        secure_flag = secure.lower() in ('1', 'true', 'yes')
    samesite = os.getenv('SESSION_COOKIE_SAMESITE', 'Lax')

    app.config['SESSION_COOKIE_HTTPONLY'] = http_only
    app.config['SESSION_COOKIE_SECURE'] = secure_flag
    # Validate samesite
    if samesite not in ('Lax', 'Strict', 'None'):
        samesite = 'Lax'
    app.config['SESSION_COOKIE_SAMESITE'] = samesite

# Apply cookie config at import time
apply_session_cookie_config()

# Expose ADMIN_SESSION_TIMEOUT via app config for templates
try:
    app.config['ADMIN_SESSION_TIMEOUT'] = int(os.getenv('ADMIN_SESSION_TIMEOUT', '0'))
except Exception:
    app.config['ADMIN_SESSION_TIMEOUT'] = 0

# Context processor to make ADMIN_SESSION_TIMEOUT available in templates
@app.context_processor
def inject_admin_config():
    # Read ADMIN_SESSION_TIMEOUT from environment at runtime so tests using monkeypatch.setenv() are respected.
    try:
        timeout = int(os.getenv('ADMIN_SESSION_TIMEOUT', '0'))
    except Exception:
        timeout = 0
    # Ensure a CSRF token exists in session and expose it to templates
    if 'csrf_token' not in session:
        session['csrf_token'] = secrets.token_urlsafe(32)
    return dict(ADMIN_SESSION_TIMEOUT=timeout, csrf_token=session.get('csrf_token'))


# Warn in production when session cookies are insecure
_flask_debug = os.getenv('FLASK_DEBUG', 'False').lower() in ('1', 'true')
if not _flask_debug and not app.config.get('SESSION_COOKIE_SECURE', True):
    logging.warning(
        "Session cookies are configured as INSECURE (SESSION_COOKIE_SECURE=False) while FLASK_DEBUG is not enabled. "
        "This is unsafe for production and may expose session cookies over plaintext HTTP."
    )

# Admin token (optional). If set, admin routes require header: Authorization: Bearer <ADMIN_TOKEN>
ADMIN_TOKEN = os.getenv('ADMIN_TOKEN')

def admin_required(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Prefer session-based admin auth when username/password are configured
        try:
            if session.get('admin_authenticated'):
                # Enforce session timeout if configured
                try:
                    timeout = int(os.getenv('ADMIN_SESSION_TIMEOUT', '0'))
                except Exception:
                    timeout = 0
                # If no timeout configured, accept session-based auth for all methods
                if not timeout:
                    return func(*args, **kwargs)
                if session.get('admin_logged_in_at'):
                    import time as _time
                    now = _time.time()
                    logged = float(session.get('admin_logged_in_at', 0))
                    logging.info("admin_required: auth=%s logged_in_at=%s timeout=%s now=%s delta=%s", session.get('admin_authenticated'), logged, timeout, now, now - logged)
                    if now - logged > timeout:
                        # session expired
                        session.pop('admin_authenticated', None)
                        session.pop('admin_username', None)
                        session.pop('admin_logged_in_at', None)
                        # For browser GETs, redirect to login; otherwise return 401
                        if request.method == 'GET' and request.accept_mimetypes.accept_html:
                            return redirect(url_for('admin_login', next=request.path))
                        return ('Unauthorized', 401, {'WWW-Authenticate': 'Bearer realm="Access to admin"'})
                    else:
                        return func(*args, **kwargs)
                else:
                    # No logged timestamp present; treat as unauthorized
                    if request.method == 'GET' and request.accept_mimetypes.accept_html:
                        return redirect(url_for('admin_login', next=request.path))
                    return ('Unauthorized', 401, {'WWW-Authenticate': 'Bearer realm="Access to admin"'})
        except RuntimeError:
            # No request context/session available; fall through to token checks
            pass

        admin_user = os.getenv('ADMIN_USERNAME')
        admin_pass = os.getenv('ADMIN_PASSWORD')
        admin_pass_hash = os.getenv('ADMIN_PASSWORD_HASH')
        token = os.getenv('ADMIN_TOKEN')

        # If username/password are configured, require session auth for web UI but accept a valid token for API
        if admin_user and (admin_pass or admin_pass_hash):
            auth = request.headers.get('Authorization', '')
            if token and auth.startswith('Bearer '):
                provided = auth.split(' ', 1)[1].strip()
                if provided == token:
                    return func(*args, **kwargs)
            # For browser GETs, redirect to login page so users can authenticate via session
            if request.method == 'GET':
                return redirect(url_for('admin_login', next=request.path))
            return ('Unauthorized', 401, {'WWW-Authenticate': 'Bearer realm="Access to admin"'})

        # If no username/password configured but ADMIN_TOKEN is present, require token
        if token:
            auth = request.headers.get('Authorization', '')
            if auth.startswith('Bearer '):
                provided = auth.split(' ', 1)[1].strip()
                if provided == token:
                    return func(*args, **kwargs)
            if request.accept_mimetypes.accept_html:
                return redirect(url_for('admin_login', next=request.path))
            return ('Unauthorized', 401, {'WWW-Authenticate': 'Bearer realm="Access to admin"'})

        # If neither admin creds nor token are configured, remain permissive (legacy behavior)
        return func(*args, **kwargs)
    return wrapper

def csrf_protect(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        if request.method == 'POST':
            token = session.get('csrf_token')
            provided = request.headers.get('X-CSRF-Token') or request.form.get('csrf_token') or (request.get_json(silent=True) or {}).get('csrf_token')
            if not token or not provided or provided != token:
                return ('Forbidden', 403)
        return func(*args, **kwargs)
    return wrapper

# Simple in-memory rate limiter for admin keepalive
ADMIN_KEEPALIVE_RATE_LIMIT = int(os.getenv('ADMIN_KEEPALIVE_RATE_LIMIT', '10'))
ADMIN_KEEPALIVE_RATE_WINDOW = int(os.getenv('ADMIN_KEEPALIVE_RATE_WINDOW', '60'))
RATE_LIMIT_STORE = {}
RATE_LIMIT_LOCK = threading.Lock()

def rate_limit_keepalive(func):
    """Rate-limit wrapper for keepalive endpoint. Uses session username or csrf token as key."""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        # Determine key (prefer session username, then csrf_token, then remote addr)
        try:
            key = session.get('admin_username') or session.get('csrf_token')
        except RuntimeError:
            key = None
        if not key:
            key = request.remote_addr or 'anon'
        now = time.time()
        # Read limits at runtime so tests can modify env vars
        try:
            limit = int(os.getenv('ADMIN_KEEPALIVE_RATE_LIMIT', str(ADMIN_KEEPALIVE_RATE_LIMIT)))
        except Exception:
            limit = ADMIN_KEEPALIVE_RATE_LIMIT
        try:
            window = int(os.getenv('ADMIN_KEEPALIVE_RATE_WINDOW', str(ADMIN_KEEPALIVE_RATE_WINDOW)))
        except Exception:
            window = ADMIN_KEEPALIVE_RATE_WINDOW
        with RATE_LIMIT_LOCK:
            dq = RATE_LIMIT_STORE.get(key)
            if not dq:
                dq = deque()
                RATE_LIMIT_STORE[key] = dq
            # remove timestamps outside window
            while dq and dq[0] <= now - window:
                dq.popleft()
            if len(dq) >= limit:
                retry_after = int(window - (now - dq[0])) if dq else window
                resp = jsonify({'error': 'rate_limited'})
                return (resp, 429, {'Retry-After': str(retry_after)})
            dq.append(now)
        return func(*args, **kwargs)
    return wrapper

def _reset_rate_limit_store():
    with RATE_LIMIT_LOCK:
        RATE_LIMIT_STORE.clear()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DOWNLOAD_DIR = os.path.join(BASE_DIR, "downloads")

PRODUCTS = {
    "starter": "starter_pack.zip",
    "pro": "pro_pack.zip",
    "premium": "premium_pack.zip"
}

# Razorpay configuration (optional). If present, a client is created and a webhook endpoint is available.
RAZORPAY_KEY_ID = os.getenv("RAZORPAY_KEY_ID")
RAZORPAY_KEY_SECRET = os.getenv("RAZORPAY_KEY_SECRET")
RAZORPAY_WEBHOOK_SECRET = os.getenv("RAZORPAY_WEBHOOK_SECRET")
razorpay_client = None
if RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/buy")
def buy():
    product = request.args.get("product", "starter")
    return render_template("buy.html", product=product)

@app.route("/success")
def success():
    product = request.args.get("product", "starter")
    return render_template("success.html", product=product)

@app.route("/download/<product>")
def download(product):
    filename = PRODUCTS.get(product)
    if not filename:
        return "Invalid product", 404
    return send_from_directory(DOWNLOAD_DIR, filename, as_attachment=True)

@app.route("/create_order", methods=["POST"])
def create_order():
    """Create a Razorpay order and persist it locally.

    POST body example: { "amount": 199, "product": "starter" }
    Returns the Razorpay order JSON.
    """
    if not razorpay_client:
        return "Razorpay not configured", 500
    data = request.get_json() or {}
    amount = int(data.get("amount", 100))  # amount in rupees
    product = data.get('product', 'starter')
    # Create order with Razorpay
    order = razorpay_client.order.create({"amount": amount * 100, "currency": "INR", "receipt": f"receipt#{int(time.time())}"})
    # Persist locally using order['id'] and amount in paise
    try:
        from utils import save_order
        save_order(order.get('id'), order.get('amount'), order.get('currency', 'INR'), order.get('receipt'), product)
    except Exception as e:
        logging.exception("Failed to persist order: %s", e)
    return jsonify(order)


@app.route('/order/<order_id>')
def order_status(order_id):
    """Return JSON with local order status (if present)."""
    try:
        from utils import get_order
        row = get_order(order_id)
        if not row:
            return jsonify({'status': 'not_found'}), 404
        keys = ['id', 'amount', 'currency', 'receipt', 'product', 'status', 'created_at', 'paid_at']
        return jsonify(dict(zip(keys, row)))
    except Exception as e:
        logging.exception("Failed to fetch order: %s", e)
        return jsonify({'error': 'internal'}), 500

@app.route("/webhook", methods=["POST"])
def webhook():
    """Razorpay webhook receiver. Verifies signature using `RAZORPAY_WEBHOOK_SECRET`, persists the event (idempotent), and optionally triggers a notification.

    Behavior:
    - Verifies signature using `razorpay.WebhookSignature.verify(payload, signature, secret)`
    - Derives a stable `event_id` (from payload where possible, otherwise SHA256 of payload)
    - Saves event via `utils.save_webhook(event_id, event_name, payload)` (returns False if already seen)
    - If event is `payment.captured` attempts to send a notification email to `EMAIL_USER`.
    """
    payload = request.get_data(as_text=True)
    signature = request.headers.get("X-Razorpay-Signature")
    if not signature:
        return "Missing signature", 400
    try:
        razorpay.WebhookSignature.verify(payload, signature, RAZORPAY_WEBHOOK_SECRET)
    except Exception as e:
        logging.warning("Webhook signature verification failed: %s", e)
        return "Invalid signature", 400
    event = request.json or {}
    logging.info("Received webhook event: %s", event.get("event"))

    # Derive an id for idempotency. Prefer embedded entity ids when available.
    event_id = None
    # Common locations: payload.payment.entity.id or payload.order.entity.id
    try:
        event_id = (event.get('payload', {})
                        .get('payment', {})
                        .get('entity', {})
                        .get('id'))
    except Exception:
        event_id = None
    if not event_id:
        try:
            event_id = (event.get('payload', {})
                            .get('order', {})
                            .get('entity', {})
                            .get('id'))
        except Exception:
            event_id = None
    if not event_id:
        import hashlib
        event_id = hashlib.sha256(payload.encode()).hexdigest()

    # Persist (idempotent)
    try:
        from utils import save_webhook, save_payment, mark_order_paid
        inserted = save_webhook(event_id, event.get('event', 'unknown'), event)
        logging.info("Webhook persisted: %s, inserted=%s", event_id, inserted)
    except Exception as e:
        logging.exception("Failed to persist webhook: %s", e)

    # Example reaction: notify on payment captured and update order/payment tables
    if event.get('event') == 'payment.captured':
        try:
            # Extract payment id and order id if provided
            payment_id = None
            order_id = None
            try:
                payment_id = event.get('payload', {}).get('payment', {}).get('entity', {}).get('id')
                order_id = event.get('payload', {}).get('payment', {}).get('entity', {}).get('order_id')
            except Exception:
                pass
            # Save payment and mark order paid if possible
            if payment_id:
                try:
                    save_payment(payment_id, order_id or event_id, event)
                except Exception:
                    pass
            if order_id:
                try:
                    updated = mark_order_paid(order_id, payment_id or event_id)
                    logging.info("Order %s marked paid=%s", order_id, updated)
                except Exception:
                    pass
        except Exception as e:
            logging.exception("Failed to process payment event: %s", e)

        # Send notification email (best-effort)
        try:
            from utils import send_email
            admin = os.getenv('EMAIL_USER')
            if admin:
                subject = f"Payment captured: {payment_id or event_id}"
                body = f"Event: {event.get('event')}\nPayment: {payment_id}\nOrder: {order_id}\nPayload: {event}"
                send_email(subject, body, admin)
                logging.info("Notification email sent to %s", admin)
        except Exception as e:
            logging.exception("Failed to send notification email: %s", e)

    return "", 200

@app.route('/admin/login', methods=['GET', 'POST'])
@csrf_protect
def admin_login():
    """Simple session-based login for admin UI using ADMIN_USERNAME/ADMIN_PASSWORD env vars."""
    admin_user = os.getenv('ADMIN_USERNAME')
    admin_pass = os.getenv('ADMIN_PASSWORD')
    admin_pass_hash = os.getenv('ADMIN_PASSWORD_HASH')
    # If credentials are not configured, allow login page to indicate how to enable it
    if request.method == 'POST':
        form_user = request.form.get('username')
        form_pass = request.form.get('password')
        logging.info("admin_login attempt: admin_user=%s admin_pass_set=%s admin_pass_hash_set=%s form_user=%s form_pass=%s", admin_user, bool(admin_pass), bool(admin_pass_hash), form_user, form_pass)
        valid = False
        if admin_user and (admin_pass or admin_pass_hash) and form_user == admin_user:
            # Prefer hashed password verification if available
            if admin_pass_hash:
                try:
                    if check_password_hash(admin_pass_hash, form_pass):
                        logging.info('admin_login: matched hashed password')
                        valid = True
                except Exception:
                    valid = False
            elif admin_pass and form_pass == admin_pass:
                logging.info('admin_login: matched plain-text password')
                valid = True
        if valid:
            session['admin_authenticated'] = True
            session['admin_username'] = admin_user
            import time as _time
            session['admin_logged_in_at'] = _time.time()
            # mark session permanent so cookie gets a max-age set; server-side timeout still enforced
            session.permanent = True
            next_url = request.args.get('next') or request.form.get('next') or url_for('admin_webhooks')
            return redirect(next_url)
        else:
            flash('Invalid credentials', 'error')
    return render_template('admin_login.html')

@app.route('/admin/logout')
def admin_logout():
    session.pop('admin_authenticated', None)
    session.pop('admin_username', None)
    return redirect(url_for('home'))

@app.route('/admin/keepalive', methods=['POST'])
@admin_required
@rate_limit_keepalive
@csrf_protect
def admin_keepalive():
    """Extend admin session (update `admin_logged_in_at`)."""
    import time as _time
    session['admin_logged_in_at'] = _time.time()
    return jsonify({'ok': True})

@app.route('/admin/webhooks')
@admin_required
def admin_webhooks():
    try:
        from utils import init_db
        init_db()
        import sqlite3
        from utils import _get_db_path

        # Filters and pagination
        event_filter = request.args.get('event')
        page = max(int(request.args.get('page', 1)), 1)
        per_page = max(int(request.args.get('per_page', 20)), 1)
        offset = (page - 1) * per_page

        conn = sqlite3.connect(_get_db_path())
        c = conn.cursor()

        where_clauses = []
        params = []
        if event_filter:
            where_clauses.append('event = ?')
            params.append(event_filter)
        where_sql = 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''

        c.execute(f'SELECT COUNT(*) FROM webhooks {where_sql}', params)
        total = c.fetchone()[0]

        c.execute(f'SELECT id, event, payload, received_at FROM webhooks {where_sql} ORDER BY received_at DESC LIMIT ? OFFSET ?', params + [per_page, offset])
        rows = c.fetchall()
        conn.close()

        return render_template('admin_webhooks.html', rows=rows, page=page, per_page=per_page, total=total, event_filter=event_filter)
    except Exception as e:
        logging.exception("Failed to render webhooks: %s", e)
        return "Internal error", 500


@app.route('/admin/orders')
@admin_required
def admin_orders():
    try:
        from utils import init_db
        init_db()
        import sqlite3
        from utils import _get_db_path

        # Filters and pagination
        product_filter = request.args.get('product')
        status_filter = request.args.get('status')
        page = max(int(request.args.get('page', 1)), 1)
        per_page = max(int(request.args.get('per_page', 20)), 1)
        offset = (page - 1) * per_page

        conn = sqlite3.connect(_get_db_path())
        c = conn.cursor()

        where_clauses = []
        params = []
        if product_filter:
            where_clauses.append('product = ?')
            params.append(product_filter)
        if status_filter:
            where_clauses.append('status = ?')
            params.append(status_filter)
        where_sql = 'WHERE ' + ' AND '.join(where_clauses) if where_clauses else ''

        c.execute(f'SELECT COUNT(*) FROM orders {where_sql}', params)
        total = c.fetchone()[0]

        c.execute(f'SELECT id, amount, currency, receipt, product, status, created_at, paid_at FROM orders {where_sql} ORDER BY created_at DESC LIMIT ? OFFSET ?', params + [per_page, offset])
        rows = c.fetchall()
        conn.close()

        return render_template('admin_orders.html', rows=rows, page=page, per_page=per_page, total=total, product_filter=product_filter, status_filter=status_filter)
    except Exception as e:
        logging.exception("Failed to render orders: %s", e)
        return "Internal error", 500


@app.route('/admin/reconcile', methods=['GET', 'POST'])
@admin_required
@csrf_protect
def admin_reconcile():
    try:
        from utils import reconcile_orders, apply_reconciliation, init_db
        init_db()
        report = reconcile_orders()
        result = None
        if request.method == 'POST':
            result = apply_reconciliation()
            # refresh report
            report = reconcile_orders()
        return render_template('admin_reconcile.html', report=report, result=result)
    except Exception as e:
        logging.exception("Failed to run reconciliation: %s", e)
        return "Internal error", 500


if __name__ == "__main__":
    debug_mode = os.getenv("FLASK_DEBUG", "True").lower() in ("1", "true")
    app.run(debug=debug_mode)
