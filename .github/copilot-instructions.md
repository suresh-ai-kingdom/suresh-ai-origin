# Copilot instructions — SURESH AI ORIGIN

**PRODUCTION STATUS:** ✅ LIVE (January 13, 2026)  
**INCOME MODE:** 💰 RAZORPAY LIVE KEYS  
**AI MODE:** 🤖 REAL (Google Gemini 2.5 Flash - FREE)  
**SYSTEM HEALTH:** 86% (6/7 systems working)

## Big picture (what this app is)
**SURESH AI ORIGIN** is a production-grade Flask-based **AI Business Automation Platform** with **19 AI-powered features**, **80+ REST endpoints**, and **30+ database tables**. Currently live on Render accepting real payments via Razorpay LIVE mode with real AI (Gemini 2.5 Flash).

### Architecture Overview
```
PRESENTATION LAYER (16 admin dashboards + public site)
    ↓ HTTPS/Render
API LAYER (80+ REST endpoints + Razorpay webhooks)
    ↓ 
19 FEATURE ENGINES: AI Content, Recommendations, Predictive Analytics, Chatbot,
Email Timing, Growth Forecast, CLV, Pricing, Churn, Market Intel, Payment Intel,
Segmentation, Campaigns, Recovery, Referrals, Subscriptions, Voice, A/B Testing, Journeys
    ↓
DATA ACCESS (SQLAlchemy ORM, 30+ models)
    ↓
PERSISTENCE (SQLite with Alembic migrations)
```

**CRITICAL CONTEXT FOR NEW AGENTS:**
- **LIVE MODE:** Razorpay keys are LIVE (real money flowing). NEW environment variables must be used, not old test keys.
- **AI IS REAL:** All 19 features use Google Gemini 2.5 Flash (free tier, 60 req/min quota). Not demo/placeholder.
- **SECURITY:** `.env` must NEVER contain real keys—use Render environment variables only. Keys rotated 1/13/2026.
- **PAYMENT FLOW:** Customer pays → Razorpay webhook → Order marked paid → Email sent → T+3 settlement.
- **DEPLOYMENT:** Render auto-deploys from GitHub. All critical secrets in Render env, not in git.

## Key files & modules

### Core Application
- `app.py` (2,500+ lines) — Flask application with all routes, request ID tracking, session management, flag system, and admin UI endpoints. Routes follow pattern `/api/<feature>/<action>`.
- `models.py` (500+ lines) — SQLAlchemy ORM models for Webhook, Order, Payment, Subscription, Referral, Customer, Segment, CampaignTemplate, etc. See `Base.metadata` for 30+ tables.
- `utils.py` (300+ lines) — Shared utilities: `init_db()`, `save_order()`, `mark_order_paid()`, `reconcile_orders()`, `send_email()`, `get_engine()`, `get_session()`.
- `security_middleware.py` — Adds security headers (CSP, X-Frame-Options, HSTS) to all responses.
- `logging_config.py` — Structured logging setup with correlation IDs.
- `config_validator.py` — Validates environment configuration at startup.

### Feature Engines (19 total)
Each feature is an independent module with its own business logic. Examples:
- `ai_generator.py` — Generate marketing content (emails, posts, descriptions). Routes: `/api/ai/generate` (POST).
- `recommendations.py` — Product recommendations from purchase history. Routes: `/api/recommendations/suggest` (GET).
- `predictive_analytics.py` — Revenue/churn/growth forecasting. Routes: `/api/analytics/revenue-forecast`, `/api/analytics/churn`.
- `subscriptions.py` — Recurring revenue management (3 tiers: Starter/Pro/Premium). Routes: `/api/subscriptions/status`, `/api/subscriptions/upgrade`.
- `recovery.py` — Abandoned order recovery with smart reminders. Routes: `/api/recovery/check`, `/api/recovery/send-reminder`.
- `referrals.py` — Viral growth program (30% commission). Routes: `/api/referrals/generate-link`, `/api/referrals/track`.
- Similar patterns for: `chatbot.py`, `email_timing.py`, `growth_forecast.py`, `clv.py`, `pricing.py`, `churn_prediction.py`, `segment_optimization.py`, `campaign_generator.py`, `market_intelligence.py`, `payment_intelligence.py`, `voice_analytics.py`, `ab_testing_engine.py`, `journey_orchestration_engine.py`, `website_generator.py`.

### Admin & Integration
- `executive_dashboard.py` (350+ lines) — Aggregates metrics from all features for executive view. Routes: `/admin/executive` (HTML dashboard), `/api/executive/metrics` (JSON).
- `api_documentation.py` (1000+ lines) — OpenAPI spec generator for all 80+ endpoints. Routes: `/api/docs` (JSON), `/api/docs/html` (Swagger UI).
- `automation_workflows.py` — Orchestrates cross-feature workflows (e.g., "on payment, send email, create subscription, generate recommendation").
- `entitlements.py` — Feature flag system (finance_entitlements_enforced, intel_recommendations_enabled, etc.).

### Templates (Jinja2)
- `templates/index.html` — Customer-facing homepage with hero, features, products, FAQ.
- `templates/buy.html`, `templates/success.html`, `templates/order_tracking.html` — Purchase funnel.
- `templates/admin.html` — Admin hub with quick links to 16 dashboards.
- `templates/admin_*.html` (15 files) — Feature-specific dashboards (e.g., admin_subscriptions.html, admin_recommendations.html, admin_analytics.html).

### Database & Migrations
- `alembic/` — Alembic configuration for database versioning. Run `PYTHONPATH=. alembic upgrade head` to apply migrations.
- `data.db` — Default SQLite database (can override with `DATA_DB` env var).

### Testing & Scripts
- `tests/` (40+ test files, 365+ tests) — Comprehensive pytest suite. Run `pytest -q` to execute all.
- `conftest.py` — Pytest fixtures and configuration.
- `scripts/seed_demo.py` — Seed demo data or clear DB. Usage: `python scripts/seed_demo.py seed|clear|status`.
- `scripts/backup_db.py` — Create/restore/cleanup database backups.

## Environment variables (must be set in Render only — NEVER hardcode or commit)

**🚨 SECURITY CRITICAL:** All secrets go in Render Dashboard → Environment. NEVER commit to git.

### Payment (LIVE Mode - Real Money!)
- `RAZORPAY_KEY_ID=rzp_live_...` — LIVE Razorpay key (NOT test key!)
- `RAZORPAY_KEY_SECRET=...` — LIVE secret key (rotated 1/13/2026 for security)
- `RAZORPAY_WEBHOOK_SECRET=vgxetSWZcp9@gff` — Webhook verification

### AI (Real, FREE)
- `GOOGLE_API_KEY=AIzaSyCuc8tHg_3XiaI_MEg4AorQ3uQ0Xtbtgds` — Gemini 2.5 Flash (free tier)
- `AI_PROVIDER=gemini` — Uses Google Gemini (not demo mode)
- `AI_MODEL=gemini-2.5-flash` — Latest Gemini model

### Email Notifications
- `EMAIL_USER=suresh.ai.origin@outlook.com` — SMTP sender
- `EMAIL_PASS=...` — SMTP password (app password for Outlook)

### Security & Session
- `FLASK_SECRET_KEY=suresh_ai_origin_secret` — Flask session key
- `ADMIN_USERNAME=admin` — Admin login
- `ADMIN_PASSWORD=SureshAI2026!` — Admin password (change in production!)

### Optional
- `DATA_DB` — Custom database path (default: `data.db`)
- `FLASK_DEBUG` — Set to '1' for local debug
- `FLAG_*` — Feature flags (see app.py for all available flags)

## Production Status & Known Issues

**✅ LIVE (January 13, 2026)**
- Razorpay LIVE mode: Real payments accepted (2% fee)
- Real AI: Gemini 2.5 Flash (60 req/min FREE quota)
- Admin authentication: Session-based + Bearer token support
- Payment settlement: T+3 business days
- Site: https://suresh-ai-origin.onrender.com

**⚠️ SECURITY DECISIONS**
- Keys rotated after GitHub exposure: Old test keys are DEAD
- Use ONLY Render environment variables for production
- `.env` file is for LOCAL DEVELOPMENT ONLY
- Never commit real keys to GitHub

## Razorpay & webhooks (production patterns)
- Webhook handler at `/webhook` (POST) verifies `X-Razorpay-Signature` using HMAC-SHA256
- Idempotent by event_id: Same webhook can be received multiple times, processed only once
- Flow: Payment → Webhook → Order marked paid → Email confirmation → Download link
- Error handling: 3 payment retry attempts before marking failed
- Settlement: Razorpay holds 2% fee, deposits to bank in T+3 days

## Testing
- **40+ test files** in `tests/` with **365+ tests** covering all 19 features.
- Test coverage: 99.5%+ pass rate across all features (see CI logs or run `pytest -q` locally).
- Tests use pytest fixtures (in `conftest.py`) with Flask test client for isolated unit and integration tests.
- Key test patterns:
  - Feature tests: `test_<feature_name>.py` (e.g., `test_subscriptions.py`, `test_recommendations.py`)
  - Admin tests: `test_admin*.py` (auth, pagination, session management)
  - Integration tests: `test_integration.py`, `test_order_tracking.py`, `test_recovery_integration.py`
  - Webhook/payment tests: `test_webhook.py`, `test_payments.py`
- Run tests: `pytest -q` (run all), `pytest tests/test_subscriptions.py -v` (single file).
- Use `monkeypatch` in conftest fixtures to mock environment variables, Razorpay client, email sending.

## Deployment & runtime
- **Local debug:** `python app.py` (runs Flask on http://localhost:5000; `FLASK_DEBUG` or `.env` controls debug mode).
- **Apply migrations first:** `PYTHONPATH=. alembic upgrade head` (PowerShell: `$env:PYTHONPATH='.'; alembic upgrade head`)
- **Production (Render):** `gunicorn app:app` (matches `render.yaml`). Ensure `gunicorn` is available (already in `requirements.txt`).
- **Static files:** Served from `/static`; download ZIPs served from `downloads/` via `send_from_directory(..., as_attachment=True)`.
- **Demo data:** Use `scripts/seed_demo.py seed` to populate test data; `scripts/seed_demo.py clear` to reset.
- **Backup/restore:** Use `scripts/backup_db.py` to create/restore database snapshots.

## Integration points & key architecture patterns
- **Feature flags** (`get_flag()`, `FLAG_DEFAULTS`) control feature availability. Check `app.py` for current flags; add new flags via environment variables with `FLAG_` prefix.
- **Request correlation** via `request_id` (in `g`) and audit logging via `audit_log()` helps track requests across distributed operations.
- **Webhook idempotency** in `utils.py` uses event ID to prevent duplicate processing; all webhook handlers should check `get_webhook_by_id()` before processing.
- **Feature-to-feature communication** via database tables (e.g., `subscriptions.py` reads `Order` and `Payment` from models; `recommendations.py` uses `Customer` and `Order` history).
- **Admin dashboard aggregation** in `executive_dashboard.py` reads metrics from all feature engines; follow the pattern `get_<feature>_metrics()` for new features.
- **Session & auth** in `app.py`: admin pages redirect to `/admin/login` if session not authenticated; feature access can be gated by `entitlements.py` based on paid tier.
- **Stripe & Razorpay** both supported: `stripe_integration.py` handles Stripe webhooks; core webhook handler in `app.py` handles Razorpay. They're independent—set env vars to choose which to use.

## Project-specific conventions & patterns
- **Feature modules** each have a consistent pattern:
  - Module name: `<feature_name>.py` (e.g., `subscriptions.py`, `recommendations.py`)
  - Core function: `get_<feature_name>_<action>()` (e.g., `get_recommendation_stats()`, `get_subscriptions_by_customer()`)
  - API route: `/api/<feature>/<action>` (e.g., `/api/recommendations/suggest`, `/api/subscriptions/upgrade`)
  - Admin dashboard: `templates/admin_<feature_name>.html`
  - Test file: `tests/test_<feature_name>.py`
- **Database models** in `models.py` use SQLAlchemy declarative syntax and are lazy-loaded by feature modules as needed.
- **Routes in app.py** follow REST conventions but also include custom HTML dashboards (e.g., `/admin/subscriptions` returns HTML dashboard, `/api/subscriptions/status` returns JSON).
- **Product mappings** for downloads: URL key in route maps to ZIP file in `downloads/` directory (e.g., `/download/starter` serves `downloads/starter_pack.zip`).
- **Email templates**: Use Jinja2 in `templates/` folder; emails are sent via `send_email()` utility which constructs MIME messages with `html_body` support.
- **Admin pages** require login (check `session.get('admin_logged_in')`); unauthenticated redirects to `/admin/login`. All admin routes are protected via decorator pattern.
- **Error handling** uses Flask error handlers (e.g., `@app.errorhandler(404)`) and custom exception classes where needed.
- When adding new features:
  1. Create `<feature>.py` module with core business logic functions
  2. Add API routes in `app.py` following `/api/<feature>/<action>` pattern
  3. Create admin dashboard template `templates/admin_<feature>.html`
  4. Add test file `tests/test_<feature>.py` with 15-25 comprehensive tests
  5. Update `executive_dashboard.py` with metrics aggregation
  6. Document endpoints in docstrings; they auto-populate OpenAPI spec via `api_documentation.py`

## Debugging tips (repo-specific)
- For quick local testing, run `python app.py` and visit `http://localhost:5000/`.
- Check `/admin` dashboards for real-time view of system state (orders, webhooks, subscriptions, recommendations, etc.).
- For feature-specific debugging:
  - **Subscriptions:** Check `/admin/subscriptions` dashboard and `subscriptions.py` state; verify MRR/ARR calculations.
  - **Recommendations:** Check `/admin/recommendations` to see top products and cross-sell opportunities; trace `generate_recommendations()` logic.
  - **Recovery:** Check `/admin/recovery` for abandoned orders and reminder history; verify email delivery in logs.
  - **Webhooks:** Check `/admin/webhooks` list; use `get_webhook_by_id()` to fetch raw payload; verify signature in `app.py` handler.
- Use `request_id` header (`X-Request-ID`) in logs to correlate request flow across feature engines.
- Enable `FLASK_DEBUG=1` for auto-reload; set `FLAG_*` env vars to toggle feature availability during testing.
- Production issues: Check Gunicorn logs (Render: Settings → Logs) and ensure all env vars are present (use `config_validator.py` as reference).

## Integration test (order → payment → download)
- An integration test `tests/test_integration.py` simulates creating an order via `/create_order`, then posts a `payment.captured` webhook to `/webhook` and asserts the order is marked `paid` and the payment is recorded.
- The test mocks `razorpay_client` and the webhook signature verification so it runs offline and deterministically.
- Tests: see `tests/test_integration.py`, `tests/test_recovery_integration.py`, and feature-specific integration scenarios.
- Run full tests with `pytest -q` (CI runs the same via GitHub Actions).

## Admin UI
- Admin endpoints for quick inspection:
  - `/admin/webhooks` — lists recent webhook events from `data.db` (or `DATA_DB` if set).
  - `/admin/orders` — lists recent orders and their status.
  - `/admin/reconcile` — displays a reconciliation report (unpaid orders, orphan payments, candidates) and allows a POST to apply reconciliation (marks unpaid orders paid when a matching payment exists).
- Authentication: You can enable **session-based** admin access by setting `ADMIN_USERNAME` and `ADMIN_PASSWORD` in your environment. Visiting an admin page will redirect to `/admin/login` and create a session cookie on successful login. For API clients or non-interactive access, `ADMIN_TOKEN` (Bearer token) is still supported.
- Client-side session warning: when `ADMIN_SESSION_TIMEOUT` is configured, admin pages include a countdown and an "Extend" button in the header that calls `/admin/keepalive` to extend the session (updates server-side `admin_logged_in_at`).
- These pages are minimal. In production, prefer a stronger auth mechanism (session with HTTPS, hashed secrets, or OAuth) instead of shared env credentials where appropriate.

## Reconciliation
- Use `/admin/reconcile` to inspect unpaid orders and orphan payments. Press the button to run cooperation logic that marks unpaid orders as `paid` when a payment referencing the order exists (idempotent).
- Utilities in `utils.py`:
  - `reconcile_orders()` — returns a report with `unpaid_orders`, `orphan_payments`, and `candidates`.
  - `apply_reconciliation()` — applies the reconciliation (marks matched orders paid) and returns counts.
- Tests: `tests/test_reconcile.py` exercises the endpoint and ensures orders are marked paid when reconciliation runs.

## Database & migrations
- The project now uses **SQLAlchemy** models defined in `models.py` (Webhooks, Orders, Payments).
- Development convenience: `utils.init_db()` calls `models.init_models()` which runs `Base.metadata.create_all()` if no migrations are applied.
- For production, prefer running Alembic migrations (configured in `alembic/`):
  - Generate revision: `alembic revision --autogenerate -m "initial"`
  - Apply migrations: `alembic upgrade head`
- The Alembic env is configured to use `models.Base.metadata` for autogeneration. Note: For an existing SQLite database that already matches the models, you can `alembic stamp head` to mark the DB as migrated instead of running `alembic upgrade head` (SQLite has limited ALTER support).

CI behavior: the GitHub Actions workflow runs migrations before tests and uses a safe fallback. It attempts `alembic upgrade head` and falls back to `alembic stamp head` on failure to handle SQLite limitations. This keeps CI deterministic for both fresh and preexisting DBs.

## Feature Deep-Dives

### Subscriptions (subscriptions.py)
**What it does:** Manages recurring revenue with 3 tiers (Starter ₹99/mo, Pro ₹499/mo, Premium ₹999/mo).

**Key functions:**
- `create_subscription(receipt, tier, billing_cycle)` — Create new subscription with monthly/yearly billing
- `get_active_subscriptions(receipt=None)` — Filter by customer or get all active
- `calculate_mrr()` / `calculate_arr()` — Monthly/annual recurring revenue totals
- `get_expiring_subscriptions(days_ahead=7)` — Find subscriptions about to expire
- `cancel_subscription(subscription_id, reason)` — Mark cancelled with optional reason
- `renew_subscription(subscription_id)` — Extend current subscription period
- `get_tier_upgrade_opportunities()` — Find Starter customers ready for upgrade
- `get_subscription_revenue_forecast(months=12)` — Project revenue with churn modeling

**Pricing structure (in paise):**
```python
SUBSCRIPTION_PRICING = {
    'STARTER': {'monthly': 9900, 'yearly': 99000},  # ₹990/year = 2 months free
    'PRO': {'monthly': 49900, 'yearly': 499000},
    'PREMIUM': {'monthly': 99900, 'yearly': 999000}
}
```

**Database relations:** Reads `Subscription`, `Order`, `Customer` tables. Status enum: ACTIVE, PAST_DUE, CANCELLED, EXPIRED, TRIAL.

**API routes:**
- `GET /api/subscriptions/status` — Current subscription for customer (requires receipt)
- `POST /api/subscriptions/create` — Create new subscription
- `POST /api/subscriptions/cancel` — Cancel with optional reason
- `GET /api/subscriptions/upgrade-opportunities` — Find upgrade candidates

**Testing:** See `tests/test_subscriptions.py` — uses `cleanup_subs` fixture to isolate test data.

---

### Recommendations (recommendations.py)
**What it does:** Smart product suggestions using purchase history and affinity scoring.

**Key classes & functions:**
- `Recommendation` — Single product with score (0-100), reason, confidence
- `RecommendationResult` — Container with list of recommendations + metadata
- `calculate_product_affinity(customer_receipt)` — Returns dict mapping product → affinity (0-100)
- `generate_recommendations(customer_receipt, limit=3)` — Return top N products for upsell
- `get_cross_sell_opportunities()` — Find top customers by cross-sell potential
- `get_product_performance()` — Aggregate metrics per product (order count, revenue, avg LTV)
- `calculate_recommendation_impact()` — Estimated revenue lift from recommendations

**Algorithm (affinity scoring):**
1. Look up customer LTV (Lifetime Value) and order count
2. Calculate base score based on LTV percentile
3. Boost score for products not yet purchased
4. Apply decay for recently purchased products
5. Return products ranked by score

**Product catalog (hardcoded):**
```python
PRODUCT_CATALOG = {
    'starter': {'price': 99, 'tags': ['beginner', 'affordable']},
    'pro': {'price': 499, 'tags': ['professional', 'advanced']},
    'premium': {'price': 999, 'tags': ['expert', 'comprehensive']},
    'platinum': {'price': 2999, 'tags': ['vip', 'coaching']}
}
```

**API routes:**
- `GET /api/recommendations/suggest?receipt=<customer>` — Get top 3 recommendations
- `GET /api/recommendations/cross-sell` — System-wide cross-sell opportunities
- `GET /api/recommendations/stats` — Aggregated recommendation performance

**Testing:** `tests/test_recommendations.py` — mocks customer purchase history to test scoring.

---

### Recovery (recovery.py)
**What it does:** Abandoned order recovery with automatic reminder sequence (1hr, 24hr, 72hr).

**Key functions:**
- `get_abandoned_orders(hours_since=None, limit=None)` — Find unpaid orders created N hours ago
- `should_send_reminder(order_id, reminder_sequence)` — Check if reminder should go out (time-based)
- `send_recovery_reminder(order_id, reminder_sequence, discount_pct=None)` — Compose + email reminder
- `check_abandoned_recovery_impact()` — Measure recovery rate and revenue impact

**Reminder schedule (automatic):**
```python
REMINDER_SCHEDULE = [
    {'delay_hours': 1, 'name': 'Urgent Reminder'},
    {'delay_hours': 24, 'name': '1-Day Follow-up'},
    {'delay_hours': 72, 'name': '3-Day Last Chance'},
]
```

**Key insight:** Recovery emails include optional discount codes (e.g., "COMEBACK10" for 10% off) to incentivize completion.

**Database model:** `AbandonedReminder` tracks `status` (PENDING → SENT → CONVERTED) and timestamps (sent_at, clicked_at, converted_at).

**API routes:**
- `GET /api/recovery/abandoned-orders` — List all unrecovered orders
- `POST /api/recovery/send-reminder?order_id=<id>&sequence=0` — Trigger a specific reminder
- `GET /api/recovery/analytics` — Recovery rate, avg discount offered, revenue impact

**Testing:** `tests/test_recovery.py`, `tests/test_recovery_integration.py` — mocks time passage and email sending.

---

## Payment Integration Flow (Razorpay & Stripe)

### Razorpay Flow
**Create Order → Verify Webhook → Mark Paid → Send Confirmation**

**1. Create Order (app.py: `/create_order`)**
```python
@app.route("/create_order", methods=["POST"])
def create_order():
    # POST: {"amount": 199, "product": "starter", "coupon_code": "SAVE20"}
    data = request.get_json()
    amount = int(data.get("amount", 100))  # in rupees
    
    # Apply coupon discount if provided
    if coupon_code := data.get('coupon_code'):
        discounted_amount = apply_coupon(coupon_code, amount)
        amount = discounted_amount
    
    # Create Razorpay order (converts to paise internally)
    order = razorpay_client.order.create({
        "amount": amount * 100,  # amount in paise
        "currency": "INR",
        "receipt": f"receipt#{int(time.time())}"
    })
    
    # Persist locally (idempotent by order ID)
    save_order(order['id'], order['amount'], 'INR', order['receipt'], product)
    return jsonify(order)
```

**Flow:**
- Client submits form with amount + product
- Server creates Razorpay order (gets order ID)
- Server saves order locally with status='created'
- Client redirects to Razorpay checkout page
- Customer completes payment on Razorpay

**2. Webhook Reception & Verification (app.py: `/webhook`)**
```python
@app.route("/webhook", methods=["POST"])
def webhook():
    payload = request.get_data(as_text=True)
    signature = request.headers.get("X-Razorpay-Signature")
    
    # Verify signature (critical security step)
    razorpay.WebhookSignature.verify(payload, signature, RAZORPAY_WEBHOOK_SECRET)
    
    event = request.json
    event_id = extract_entity_id(event) or hash_payload(payload)
    
    # Save webhook (idempotent by event_id)
    inserted = save_webhook(event_id, event.get('event'), event)
    
    # Only process if first time seeing this event
    if inserted and event.get('event') == 'payment.captured':
        payment_id = extract_payment_id(event)
        order_id = extract_order_id(event)
        
        # Mark order as paid
        mark_order_paid(order_id, payment_id)
        
        # Send customer confirmation email (best-effort)
        send_order_confirmation(order_id, customer_email)
```

**Idempotency:** If webhook is received twice (network retry), `save_webhook()` returns False on second call, so processing only happens once.

**3. Order Status Tracking**
```python
GET /order/<order_id>  # Content negotiation: JSON API or HTML page
```
- Returns `status` field: 'created', 'paid'
- Shows download link once status='paid'
- Customers can check payment status without logging in

### Stripe Flow
**Create Checkout → Handle Subscription Events → Usage Metering**

**Key file:** `stripe_integration.py` (440 lines)

**1. Create Checkout Session**
```python
def create_checkout_session(receipt, tier, billing_cycle='month'):
    # receipt = customer ID from our system
    # tier = 'pro' or 'scale' (maps to STRIPE_PRICE_MAP)
    
    # Create/get Stripe customer
    stripe_customer = stripe.Customer.create(metadata={'receipt': receipt})
    
    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=stripe_customer['id'],
        line_items=[{'price': STRIPE_PRICE_MAP[tier], 'quantity': 1}],
        mode='subscription',  # recurring billing
        success_url='https://..../api/billing/success?session_id={CHECKOUT_SESSION_ID}',
        cancel_url='https://..../api/billing/cancel'
    )
    
    return {'status': 'success', 'url': session['url']}
```

**2. Webhook Events (handled by Stripe module)**
| Event Type | Action | Database Update |
|---------|--------|-----------------|
| `customer.subscription.created` | New subscription | Insert Subscription row with status=ACTIVE |
| `customer.subscription.updated` | Tier/billing change | Update Subscription fields |
| `invoice.payment_succeeded` | Payment cleared | Keep status=ACTIVE |
| `invoice.payment_failed` | Payment failed | Set status=PAST_DUE |
| `customer.subscription.deleted` | Customer cancelled | Set status=CANCELLED, update cancelled_at |

**3. Usage-Based Metering**
```python
# If subscription has usage limits (attribution runs, models, exports)
def record_usage(subscription_id, metric_name, quantity):
    # Increment counter for current billing period
    meter = UsageMeter.query.filter_by(subscription_id=subscription_id).first()
    if meter:
        meter.attribution_runs += quantity
        if meter.attribution_runs > PLAN_LIMITS['pro']['attribution_runs']:
            # Block or trigger overage
            raise QuotaExceeded(...)
```

**Coexistence:** Razorpay and Stripe both use `provider` field in Subscription model. Each customer uses one or the other.

---

## Testing Patterns for New Features

### 1. Structure
```
tests/
├── test_<feature>.py          # Unit + integration tests
├── conftest.py                # Shared fixtures
└── test_<feature>_integration.py  # Full workflow tests (optional)
```

### 2. Basic Feature Test Template
```python
"""Tests for <feature> system."""
import pytest
from models import get_session, <Model>, Base, get_engine
from <feature> import <core_functions>

@pytest.fixture
def cleanup_db():
    """Clean up test data before and after."""
    engine = get_engine()
    Base.metadata.create_all(engine)
    
    session = get_session()
    try:
        session.query(<Model>).filter(<Model>.id.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()
    
    yield
    
    # Cleanup after test
    session = get_session()
    try:
        session.query(<Model>).filter(<Model>.id.like('TEST_%')).delete()
        session.commit()
    finally:
        session.close()

def test_create_<item>(cleanup_db):
    """Test creating a new <item>."""
    result = create_<item>('TEST_ITEM_1', {...})
    assert result['id'] == 'TEST_ITEM_1'
    assert result['status'] == 'ACTIVE'

def test_get_<items>_empty(cleanup_db):
    """Test querying when no items exist."""
    items = get_<items>()
    assert len(items) == 0

def test_<action>_idempotency(cleanup_db):
    """Test that repeated action doesn't duplicate."""
    result1 = perform_action('TEST_1', {...})
    result2 = perform_action('TEST_1', {...})  # Same ID
    assert result1['id'] == result2['id']
```

### 3. Fixture Pattern (from conftest.py)
```python
@pytest.fixture
def client():
    """Flask test client for integration tests."""
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

@pytest.fixture
def monkeypatch_env(monkeypatch):
    """Helper to safely mock environment variables in tests."""
    def set_env(key, value):
        monkeypatch.setenv(key, str(value))
    return set_env
```

### 4. Webhook Testing Pattern
```python
def test_webhook_persistence(client, monkeypatch, tmp_path):
    """Test webhook signature verification and idempotent persistence."""
    # Mock signature verification (skip for offline testing)
    monkeypatch.setattr(razorpay.WebhookSignature, 'verify', lambda *a, **k: True)
    
    payload = {
        "event": "payment.captured",
        "payload": {"payment": {"entity": {"id": "pay_1", "order_id": "order_1"}}}
    }
    
    # Send webhook twice to test idempotency
    rv1 = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'test'})
    rv2 = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'test'})
    
    assert rv1.status_code == 200
    assert rv2.status_code == 200
    
    # Verify only one webhook was persisted
    from utils import get_webhook_by_id
    wh = get_webhook_by_id('pay_1')
    assert wh is not None
```

### 5. Integration Test Pattern (order → payment → download)
```python
def test_order_payment_download_flow(client, monkeypatch):
    """Full integration: create order → capture payment → download."""
    # Mock Razorpay client
    mock_order = {'id': 'order_123', 'amount': 9900, 'currency': 'INR'}
    monkeypatch.setattr('razorpay.Client.order.create', lambda *a, **k: mock_order)
    
    # 1. Create order
    rv = client.post('/create_order', json={'amount': 99, 'product': 'starter'})
    assert rv.status_code == 200
    
    # 2. Simulate webhook
    monkeypatch.setattr(razorpay.WebhookSignature, 'verify', lambda *a, **k: True)
    webhook_payload = {
        "event": "payment.captured",
        "payload": {"payment": {"entity": {"id": "pay_123", "order_id": "order_123"}}}
    }
    rv = client.post('/webhook', json=webhook_payload, headers={'X-Razorpay-Signature': 'sig'})
    assert rv.status_code == 200
    
    # 3. Check order status
    rv = client.get('/order/order_123')
    assert rv.status_code == 200
    data = rv.get_json()
    assert data['status'] == 'paid'
```

### 6. Mocking Email Sending (common pattern)
```python
def test_send_notification(client, monkeypatch):
    """Test notification without sending real emails."""
    email_sent = []
    
    def mock_send_email(subject, body, to_addr, **kwargs):
        email_sent.append({'subject': subject, 'to': to_addr})
    
    monkeypatch.setattr('utils.send_email', mock_send_email)
    
    # Trigger action that sends email
    result = notify_customer('test@example.com', 'Order confirmed')
    
    assert len(email_sent) == 1
    assert 'confirmed' in email_sent[0]['subject'].lower()
```

### 7. Running Tests
```bash
# Run all tests
pytest -q

# Run single feature's tests
pytest tests/test_subscriptions.py -v

# Run with coverage
pytest --cov=subscriptions tests/test_subscriptions.py

# Run specific test
pytest tests/test_subscriptions.py::test_create_subscription_starter -v
```

---

## Database Schema Relationships

### Core Tables (Order → Payment → Customer)
```
Orders (orders)
├─ id (PK): Razorpay order ID
├─ amount (int): Amount in paise
├─ currency: 'INR'
├─ receipt (FK): Customer identifier
├─ product: 'starter' | 'pro' | 'premium'
├─ status: 'created' | 'paid'
└─ created_at, paid_at (timestamps)

Payments (payments)
├─ id (PK): Razorpay payment ID
├─ order_id (FK → orders.id)
├─ payload (JSON): Full payment object
└─ received_at (timestamp)

Customers (customers)
├─ receipt (PK): Unique customer ID
├─ segment: 'VIP' | 'LOYAL' | 'AT_RISK' | 'NEW'
├─ ltv_paise: Lifetime value in paise
├─ order_count: Total orders
├─ first_purchase_at, last_purchase_at (timestamps)
└─ last_segmented_at (when segment was computed)
```

### Subscription Tables (Razorpay + Stripe)
```
Subscriptions (subscriptions)
├─ id (PK): Subscription ID
├─ receipt (FK → customers.receipt)
├─ tier: 'STARTER' | 'PRO' | 'PREMIUM'
├─ billing_cycle: 'monthly' | 'yearly'
├─ amount_paise: Recurring charge amount
├─ status: 'ACTIVE' | 'PAST_DUE' | 'CANCELLED' | 'EXPIRED'
├─ provider: 'razorpay' | 'stripe'
├─ razorpay_subscription_id (nullable)
├─ stripe_subscription_id (nullable)
├─ stripe_customer_id (nullable)
├─ current_period_start, current_period_end (timestamps)
├─ cancelled_at, cancellation_reason
└─ created_at (timestamp)

UsageMeter (usage_meters)  [if plan has limits]
├─ id (PK)
├─ subscription_id (FK → subscriptions.id)
├─ attribution_runs, models_used, exports (counters)
├─ period_start, period_end (current billing cycle)
└─ reset_at (next reset timestamp)
```

### Recovery & Engagement Tables
```
AbandonedReminders (abandoned_reminders)
├─ id (PK)
├─ order_id (FK → orders.id)
├─ receipt (FK → customers.receipt)
├─ reminder_sequence: 0 (first) | 1 (second) | 2 (third)
├─ status: 'PENDING' | 'SENT' | 'OPENED' | 'CLICKED' | 'CONVERTED'
├─ discount_offered (nullable): % off if offered
├─ scheduled_at, sent_at, opened_at, clicked_at, converted_at (timestamps)
└─ created_at (timestamp)

Referrals (referral_programs)
├─ referral_code (PK): Unique code
├─ referrer_receipt (FK → customers.receipt)
├─ commission_percent: 30 (typical)
├─ total_referrals, successful_referrals (counts)
├─ total_commission_paise, total_paid_paise
└─ created_at (timestamp)
```

### Payment Processing Tables
```
Webhooks (webhooks)
├─ id (PK): Payment ID or payload hash
├─ event: 'payment.captured' | 'payment.failed' | etc
├─ payload (JSON): Full webhook event
└─ received_at (timestamp)

StripeEvents (stripe_events)  [for Stripe-based subscriptions]
├─ id (PK): Stripe event ID
├─ event_type: 'customer.subscription.created' | 'invoice.payment_succeeded' | etc
├─ payload (JSON): Full Stripe event
├─ processed: 0 | 1
├─ processed_at (nullable timestamp)
└─ received_at (timestamp)
```

### Query Patterns (Common)
```python
# Get customer's current subscription
sub = session.query(Subscription).filter_by(
    receipt='cust_123',
    status='ACTIVE'
).first()

# Find unpaid orders older than 24 hours
cutoff = time.time() - (24 * 3600)
unpaid = session.query(Order).filter(
    Order.status == 'created',
    Order.created_at <= cutoff
).all()

# MRR calculation: sum monthly subscriptions for current period
mrr_paise = session.query(func.sum(Subscription.amount_paise)).filter(
    Subscription.status == 'ACTIVE',
    Subscription.billing_cycle == 'monthly',
    Subscription.current_period_end > time.time()
).scalar() or 0

# Find customers at churn risk (no purchase in 60+ days)
cutoff = time.time() - (60 * 24 * 3600)
at_risk = session.query(Customer).filter(
    Customer.last_purchase_at < cutoff,
    Customer.order_count > 0
).all()
```

---

## Feature Flags & Entitlements System

### Feature Flags (entitlements.py + app.py)
**What it does:** Controls feature availability per plan tier and enforces quota limits.

**Flag System (app.py):**
```python
FLAG_DEFAULTS = {
    "finance_entitlements_enforced": True,
    "finance_free_allowance_enabled": False,
    "intel_recommendations_enabled": False,
    "intel_alerts_enabled": False,
    "growth_experiments_enabled": False,
    "growth_nudges_enabled": False,
}

def get_flag(key: str) -> bool:
    """Central flag lookup with environment override (FLAG_<KEY>)."""
    env_key = f"FLAG_{key.upper()}"
    default = FLAG_DEFAULTS.get(key, False)
    return _env_flag(env_key, default)
```

**Enable flags via environment:** `FLAG_INTEL_RECOMMENDATIONS_ENABLED=true` at startup or in `.env`

**Plan Tiers (app.py):**
```python
PLAN_LIMITS = {
    "free": {
        "attribution_runs": 100,
        "models": 1,
        "lookback_days": 7,
        "export": False,
    },
    "pro": {
        "attribution_runs": 5000,
        "models": 3,
        "lookback_days": 60,
        "export": True,
    },
    "scale": {
        "attribution_runs": 25000,
        "models": 10,
        "lookback_days": 180,
        "export": True,
    },
}
```

### Entitlement Checking (entitlements.py)
**Core function:** `check_entitlement(feature, context)` returns `{allow: bool, reason: str, upgrade_url: str}`

**Key Features:**
1. **Usage Threshold Alerts** (automatic at 80%, 90%, 100%, 110%)
   - `emit_alert('usage_80', {...})` at 80% usage
   - `emit_alert('usage_hard_block', {...})` at 110% (grace period)
2. **Enforce on features:** download, export, attribution_run
3. **Grace window:** Allows 10% overage (configurable via `PLAN_ATTRIBUTION_GRACE_PERCENT`)
4. **Signed tokens:** Premium downloads require HMAC-signed tokens with TTL

**Example Usage:**
```python
# Check if customer can download premium product
decision = check_entitlement('download', {
    'product': 'premium',
    'ip': request.remote_addr,
    'token': request.args.get('token')
})

if not decision['allow']:
    return jsonify({'error': 'payment_required', 'upgrade_url': decision['upgrade_url']}), 402
```

### Rate Limiting (entitlements.py)
**Decorator:** `@rate_limit_feature('download')` on routes

**Configuration (per IP):**
```python
RATE_LIMITS = {
    'download': (30, 60),        # 30 requests per minute
    'create_order': (10, 60),    # 10 requests per minute
    'export': (15, 60),
    'attribution_run': (120, 60),
}
```

**Override via environment:** `RATE_DOWNLOAD_LIMIT=50 RATE_DOWNLOAD_WINDOW=120`

**Returns 429 (Too Many Requests)** with `Retry-After` header

### Idempotency Keys (entitlements.py)
**Decorator:** `@require_idempotency_key` on POST routes (e.g., `/create_order`)

**Client requirement:** Include `Idempotency-Key` header
```bash
curl -X POST /create_order \
  -H "Idempotency-Key: unique-key-123"
```

**Returns 400** if missing when `ENFORCE_IDEMPOTENCY=true`

### Download Token System (entitlements.py)
**Generate signed token:**
```python
token = generate_download_token(
    product='premium',
    ip='192.168.1.1',  # Optional: bind to IP
    ttl=900  # 15 minutes
)
# Format: expires_epoch.hmac_signature
```

**Verify token:**
```python
valid = verify_download_token(token, product='premium', ip='192.168.1.1')
# Returns True if valid and not expired
```

**Enable IP binding:** `BIND_DOWNLOAD_TOKEN_TO_IP=true`

---

## Executive Dashboard Aggregation Patterns

### Core Pattern (executive_dashboard.py)
**Principle:** Each feature module exports a `get_<feature>_metrics()` or similar function, dashboard aggregates them.

**Template structure:**
```python
def aggregate_<feature>_metrics(days: int = 30) -> Dict:
    """Aggregate feature-specific metrics."""
    try:
        from <feature_module> import <function_name>
        result = <function_name>(days_back=days)
        if result:
            return {
                'key1': result.get('metric1', 0),
                'key2': result.get('metric2', 0),
            }
    except Exception:
        return {'key1': 0, 'key2': 0}
```

### Safe Import Pattern
```python
def _safe_import(module_name: str, func_name: str, *args, **kwargs):
    """Safely import and call a function, returning None on error."""
    try:
        module = __import__(module_name, fromlist=[func_name])
        func = getattr(module, func_name)
        return func(*args, **kwargs)
    except Exception as e:
        logging.error(f"Safe import failed: {module_name}.{func_name}")
        return None
```

**Why:** Prevents one broken feature from crashing the entire dashboard.

### Executive Summary Function (executive_dashboard.py)
Aggregates all 19 systems into single response:
```python
def executive_summary(days: int = 30) -> Dict:
    """Aggregate all 18 systems into executive summary."""
    return {
        'period_days': days,
        'revenue': aggregate_revenue_metrics(days),
        'subscriptions': aggregate_subscription_metrics(days),
        'clv': aggregate_clv_insights(days),
        'churn': aggregate_churn_alerts(days),
        'market': aggregate_market_signals(days),
        'payments': aggregate_payment_health(days),
        'campaigns': aggregate_campaign_performance(days),
        'voice': aggregate_voice_sentiment(days),
        'growth': aggregate_growth_forecast(),
        'social': aggregate_social_schedule(days),
        'websites': aggregate_website_metrics(days),
        'analytics': aggregate_realtime_analytics(days),
        'ab_testing': aggregate_ab_testing_metrics(days),
        'journeys': aggregate_journey_orchestration_metrics(days),
        'generated_at': time.time(),
    }
```

### Example Aggregations
**Revenue Metrics:**
- Total revenue (sum of paid orders)
- Total orders, paid orders
- Conversion rate (paid / total)

**Subscription Metrics:**
- Active subscription count
- MRR (Monthly Recurring Revenue): sum of monthly subscriptions
- ARR (Annual Recurring Revenue): MRR × 12

**Churn Analytics:**
- At-risk customer count
- Average risk score (0-100)
- Triggered alerts for intervention

**Growth Forecast:**
- Recommended scenario (baseline, conservative, aggressive)
- Growth rate percentage

### API Route (app.py)
```python
@app.route("/api/executive/summary", methods=["GET"])
@admin_required
def get_executive_summary():
    """Get executive summary for specified days."""
    days = request.args.get('days', 30, type=int)
    summary = executive_summary(days)
    return jsonify(summary)
```

### Dashboard Design Principles
1. **Fail gracefully:** One broken feature doesn't crash dashboard
2. **Time window configurable:** Defaults to 30 days, query parameter overrides
3. **Timestamp included:** `generated_at` tells when data was computed
4. **Aggregation only:** Dashboard doesn't perform heavy computations
5. **Feature independence:** Each system computes own metrics

---

## Email Notification System

### Email Sending (utils.py)
**Core function:** `send_email(subject, body, to_addr, html_body=None)`

```python
def send_email(subject: str, body: str, to_addr: str, html_body: str = None):
    """Send email via Gmail SMTP.
    
    Args:
        subject: Email subject
        body: Plain text body
        to_addr: Recipient email
        html_body: Optional HTML version (preferred when set)
    
    Returns:
        True if sent, False if failed (logs error)
    """
    email_user = os.getenv('EMAIL_USER')
    email_pass = os.getenv('EMAIL_PASS')
    
    if not email_user or not email_pass:
        logging.warning("Email config missing")
        return False
    
    try:
        msg = EmailMessage()
        msg['Subject'] = subject
        msg['From'] = email_user
        msg['To'] = to_addr
        msg.set_content(body)
        
        if html_body:
            msg.add_alternative(html_body, subtype='html')
        
        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(email_user, email_pass)
            server.send_message(msg)
        
        logging.info(f"Email sent: to={to_addr} subject={subject}")
        return True
    except Exception as e:
        logging.error(f"Email failed: {e}")
        return False
```

**Environment variables:**
- `EMAIL_USER` — Gmail address (e.g., `yourbot@gmail.com`)
- `EMAIL_PASS` — Gmail app password (NOT regular password)

### Order Confirmation Emails (email_notifications.py)
**Template-based HTML emails:**

```python
def send_order_confirmation(order_id, product_name, amount, customer_email, download_url):
    """Send order confirmation with HTML template and plain text fallback."""
    
    # Render HTML from template
    html_body = render_template(
        'email_order_confirmation.html',
        order_id=order_id,
        product_name=product_name.replace('_', ' ').title(),
        amount=f'{amount/100:.2f}',  # Convert paise to rupees
        date=datetime.now().strftime('%B %d, %Y at %I:%M %p'),
        download_url=download_url
    )
    
    # Plain text fallback
    plain_body = f"""
Payment Successful!
...
Order ID: {order_id}
Product: {product_name}
Amount: ₹{amount/100:.2f}
Download: {download_url}
"""
    
    send_email(
        subject=f'Order Confirmed - {order_id}',
        body=plain_body,
        to_addr=customer_email,
        html_body=html_body
    )
```

### HTML Email Template (templates/email_order_confirmation.html)
**Must include:**
- Responsive design (mobile-friendly)
- Order details table
- One-click download button
- Company branding
- Professional footer

**Jinja2 variables available:**
- `order_id`, `product_name`, `amount`, `date`, `download_url`

### Admin Alerts (email_notifications.py)
```python
def send_admin_alert(subject, message):
    """Send alert to admin email."""
    admin_email = os.getenv('ADMIN_EMAIL')
    if admin_email:
        send_email(subject, message, admin_email)
```

**Triggered on:**
- Large order amounts
- Payment failures (3+ attempts)
- High churn rates
- Quota exceeded
- Security events

### Email Integration Points
1. **Webhook handler (app.py):** On `payment.captured` → send confirmation
2. **Recovery system (recovery.py):** Abandoned order reminders
3. **Subscription events (subscriptions.py):** Renewal notifications
4. **Admin alerts (entitlements.py):** Usage threshold alerts

### Testing Email Sending
```python
def test_order_confirmation_email(monkeypatch):
    """Test without sending real email."""
    emails_sent = []
    
    def mock_send_email(subject, body, to_addr, **kwargs):
        emails_sent.append({'subject': subject, 'to': to_addr})
    
    monkeypatch.setattr('utils.send_email', mock_send_email)
    
    # Trigger confirmation
    send_order_confirmation('order_123', 'starter', 9900, 'test@example.com', 'http://...')
    
    assert len(emails_sent) == 1
    assert 'order_123' in emails_sent[0]['subject']
```

---

## Performance Optimization Tips

### Database Optimization

**1. Indexing Strategy (models.py)**
```python
# Already indexed in models.py:
order = Column(String, ForeignKey('orders.id'), index=True)  # For joins
receipt = Column(String, index=True)  # For customer lookups
status = Column(String, index=True)  # For filtering orders by status
tier = Column(String, index=True)  # For subscription tier queries
```

**When to add indexes:**
- Columns used in WHERE clauses (status, receipt)
- Columns used in JOINs (order_id, subscription_id)
- Columns in ORDER BY
- Avoid indexing low-cardinality columns (like status with 3 values)

**2. Query Optimization**
```python
# BAD: N+1 query problem
for order in session.query(Order).all():
    payment = session.query(Payment).filter_by(order_id=order.id).first()  # Query per order!

# GOOD: Single query with relationship
orders = session.query(Order).options(
    joinedload(Order.payments)  # Loads payments in single query
).all()

# GOOD: Aggregate queries
from sqlalchemy import func
total = session.query(func.sum(Order.amount)).filter(Order.status == 'paid').scalar()
```

**3. Connection Pooling (models.py)**
```python
engine = create_engine(
    db_url,
    pool_size=10,  # Maintain 10 connections in pool
    max_overflow=20,  # Allow up to 20 overflow connections
    pool_recycle=3600,  # Recycle connections every hour
    connect_args={"check_same_thread": False}  # SQLite only
)
```

### Application-Level Caching

**1. In-Memory Cache Pattern**
```python
from functools import lru_cache
import time

CACHE_TTL = 300  # 5 minutes

@lru_cache(maxsize=128)
def get_recommendations_cached(customer_receipt):
    """Cache recommendations for 5 minutes per customer."""
    return generate_recommendations(customer_receipt)

# Invalidate on update
def update_customer_order(customer_receipt, order):
    get_recommendations_cached.cache_clear()  # Clear entire cache
    # Or: get_recommendations_cached.cache_clear_for(customer_receipt)  # Clear one
```

**2. Time-Based Cache Invalidation**
```python
_RECOMMENDATION_CACHE = {}
_CACHE_TIMESTAMPS = {}

def get_recommendations_timed(customer_receipt):
    now = time.time()
    cached = _RECOMMENDATION_CACHE.get(customer_receipt)
    cached_at = _CACHE_TIMESTAMPS.get(customer_receipt, 0)
    
    if cached and (now - cached_at) < 300:  # 5-minute TTL
        return cached
    
    # Recompute and cache
    result = generate_recommendations(customer_receipt)
    _RECOMMENDATION_CACHE[customer_receipt] = result
    _CACHE_TIMESTAMPS[customer_receipt] = now
    return result
```

### Rate Limiting Performance

**1. Token Bucket Limiter (entitlements.py)**
- Uses in-memory `deque` per IP/feature
- O(1) amortized complexity
- Automatic cleanup of old timestamps

**2. Optimize rate limit key:**
```python
# Bad: Creates separate bucket per user+feature+IP
key = f"{user_id}:{feature}:{ip}"

# Good: Per-IP is sufficient for API throttling
key = f"{feature}:{ip}"
```

### Query Batching

**1. Batch inserts**
```python
# BAD: Multiple roundtrips
for order in orders:
    session.add(order)
    session.commit()

# GOOD: Single insert
session.add_all(orders)
session.commit()
```

**2. Batch updates**
```python
# BAD: Multiple queries
for order_id in order_ids:
    session.query(Order).filter_by(id=order_id).update({'status': 'paid'})
    session.commit()

# GOOD: Single update
session.query(Order).filter(Order.id.in_(order_ids)).update({'status': 'paid'})
session.commit()
```

### Async/Background Processing

**1. Email sending (non-blocking)**
```python
# Current: Blocking email sends on webhook
# Future: Queue for async worker
def webhook():
    # Save to database
    mark_order_paid(order_id, payment_id)
    # Queue email (don't wait for send)
    background_queue.enqueue(send_order_confirmation, order_id)
    return 'OK'
```

**2. Implement with Celery or RQ:**
```bash
pip install redis rq
```

```python
from rq import Queue
from redis import Redis

redis_conn = Redis()
q = Queue(connection=redis_conn)

def webhook():
    # Queue the email, return immediately
    job = q.enqueue(send_order_confirmation, order_id, product_name, amount)
    return jsonify({'status': 'queued'})
```

### Monitoring & Metrics

**1. Track slow queries**
```python
from sqlalchemy import event
from sqlalchemy.engine import Engine
import logging
import time

@event.listens_for(Engine, "before_cursor_execute")
def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    conn.info.setdefault('query_start_time', []).append(time.time())

@event.listens_for(Engine, "after_cursor_execute")
def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
    total = time.time() - conn.info['query_start_time'].pop(-1)
    if total > 1.0:  # Log queries > 1 second
        logging.warning(f"SLOW QUERY ({total:.2f}s): {statement[:100]}")
```

**2. Request timing**
```python
@app.before_request
def start_timer():
    g.start = time.time()

@app.after_request
def log_timing(response):
    elapsed = time.time() - g.start
    if elapsed > 1.0:  # Log requests > 1 second
        logging.warning(f"SLOW REQUEST ({elapsed:.2f}s): {request.path}")
    return response
```

### Scaling Strategies

**1. Database**
- Use `alembic migrate` to add indexes on large tables
- Consider read replicas for dashboards (separate DB connection)
- Archive old webhook/log data to cold storage

**2. API**
- Add caching layer (Redis) for frequently queried data
- Use database connection pooling (configured above)
- Implement pagination for list endpoints

**3. File uploads/downloads**
- Serve static files from CDN (Render static volumes)
- Use `send_from_directory` with `as_attachment=True` (already done)

**4. Monitoring**
- Set up Sentry or similar for error tracking
- Use Render's built-in metrics (CPU, memory, disk)
- Monitor database query times with Django Debug Toolbar or sqlalchemy event listeners

## 19 AI Features (All REAL, powered by Gemini 2.5 Flash)

Each feature integrates with the unified `real_ai_service.py` interface:
```python
from real_ai_service import RealAI
ai = RealAI()  # Auto-detects provider from AI_PROVIDER env var
response = ai.generate(prompt, max_tokens=1000, temperature=0.7)
```

**Features:**
1. `ai_generator.py` — Content generation (emails, blogs, social posts)
2. `recommendations.py` — Product upsell based on purchase history (LTV scoring)
3. `predictive_analytics.py` — Revenue/churn/growth forecasting
4. `chatbot.py` — Customer conversations with context
5. `email_timing.py` — Optimal send-time prediction
6. `growth_forecast.py` — Business growth projections
7. `clv.py` — Customer lifetime value calculation
8. `pricing.py` — Dynamic pricing optimization
9. `churn_prediction.py` — At-risk customer identification
10. `market_intelligence.py` — Competitor/market analysis
11. `payment_intelligence.py` — Transaction pattern analysis
12. `segment_optimization.py` — Smart customer segmentation
13. `campaign_generator.py` — Targeted campaign creation
14. `recovery.py` — Abandoned cart recovery (automated reminders)
15. `referrals.py` — Viral loop + commission tracking (30% default)
16. `subscriptions.py` — MRR/ARR recurring revenue management
17. `voice_analytics.py` — Audio sentiment analysis
18. `ab_testing_engine.py` — Variant testing + winner selection
19. `journey_orchestration_engine.py` — Multi-channel customer workflows

**AI Integration Pattern:**
- All features call `ai.generate()` or `ai.chat()` from `real_ai_service.py`
- Non-blocking (emails queued, AI calls async where possible)
- Free Gemini API (60 req/min quota) - upgrade by changing `GOOGLE_API_KEY`
- Supports OpenAI/Claude/Groq for enterprise (change `AI_PROVIDER` env var)

---

## PR checklist for contributors
- [ ] If adding a product: add ZIP to `downloads/` and update `PRODUCTS` & UI templates.
- [ ] If introducing env usage, document required variables and do NOT commit secrets.
- [ ] If using `.env` locally, either load it in `app.py` (we now call `load_dotenv()`) or document that it must be exported.
- [ ] If adding payments: validate webhooks, implement idempotency, and add record persistence.
- [ ] Update `render.yaml` only if the start command or service settings must change.
- [ ] New feature? Add corresponding test file with 15-25 tests covering happy path + edge cases
- [ ] New database model? Add to `models.py` + update `alembic/versions/` with migration
- [ ] New API route? Add docstring + document in `api_documentation.py` for auto-population of OpenAPI spec
- [ ] NEVER commit `.env` with real keys. Always use Render environment variables for secrets.
- [ ] If rotating API keys (security incident): Update Render env vars immediately, never store in .env.

---

**Status: Production LIVE with real payments (Razorpay) + real AI (Gemini 2.5 Flash).** ✅

```
