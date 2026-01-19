# Copilot Instructions — SURESH AI ORIGIN

**STATUS:**  LIVE (Jan 19, 2026) |  RAZORPAY LIVE |  GEMINI 2.5 FLASH (REAL) |  86% HEALTH

## Architecture at a Glance

**Flask-based AI Business Automation Platform**: 19+ feature engines (subscriptions, recommendations, recovery, predictive analytics, etc.)  SQLAlchemy ORM (30+ models)  SQLite (Alembic) on Render.

**Critical Production Context:**
-  **LIVE KEYS:** Razorpay keys are LIVE (real $ flowing). Keys rotated 1/13/2026 after GitHub exposure.
-  **REAL AI:** Gemini 2.5 Flash in production (60 req/min quota). Code defaults to Claude Opus 4.5 but production uses Gemini via `real_ai_service.py`.
-  **SECRETS:** Never commit .env with real keys. Use Render environment only.
- **Webhook Flow:** Payment  `/webhook` handler  Order marked paid  Email  Download link.

## Project Structure

```
.
├── app.py                    # Main Flask app (7,342L): routes, webhooks, admin UI
├── models.py                 # SQLAlchemy ORM (659L): 30+ models
├── utils.py                  # Core helpers (197L): DB, email, order management
├── real_ai_service.py        # Unified AI interface (304L)
├── entitlements.py           # Feature flags & rate limiting (239L)
├── executive_dashboard.py    # Metrics aggregation (354L)
│
├── Feature Engines (276 Python files total)
│   ├── subscriptions.py      # Recurring revenue management
│   ├── recommendations.py    # ML-based suggestions
│   ├── recovery.py           # Abandoned cart recovery
│   ├── predictive_analytics.py
│   ├── ai_generator.py       # AI content generation
│   ├── analytics.py          # Usage analytics
│   └── ... (19+ more engines)
│
├── scripts/                  # Operational scripts
│   ├── seed_demo.py          # Database seeding
│   ├── backup_db.py          # Database backups
│   └── ...
│
├── tests/                    # 415+ tests in 62 files
│   ├── conftest.py           # Pytest fixtures
│   └── test_*.py             # Feature-specific tests
│
├── templates/                # Jinja2 templates
│   ├── admin_*.html          # 48+ admin dashboards
│   └── email_*.html          # Email templates
│
├── alembic/                  # Database migrations
│   └── versions/             # Migration scripts
│
└── .github/
    └── copilot-instructions.md  # This file
```

## Developer Workflows

### Quick Start
```bash
# Local dev (auto-reload)
FLASK_DEBUG=1 python app.py         # http://localhost:5000

# Migrations
PYTHONPATH=. alembic upgrade head    # Apply DB migrations
python scripts/seed_demo.py seed     # Populate test data

# Database backups
python scripts/backup_db.py create   # Create timestamped backup
python scripts/backup_db.py restore  # Restore most recent

# Tests
pytest -q                             # Run all (415+ tests across 62 files)
pytest tests/test_subscriptions.py -v # Single feature
```

### Debug Checklist
1. **Payment issues?**  Check `/admin/webhooks` for webhook events, verify `X-Razorpay-Signature`
2. **Feature not working?**  Check `FLAG_*` environment variables (e.g., `FLAG_RECOMMENDATIONS_ENABLED`)
3. **Database locked?**  Restart: `rm data.db && python scripts/seed_demo.py seed`
4. **Email not sending?**  Verify `EMAIL_USER`/`EMAIL_PASS` in Render env (app password for Outlook, not regular password)

## Project-Specific Patterns

### Feature Engine Pattern
Every feature module (`ai_generator.py`, `subscriptions.py`, etc.) follows:
```
<feature_name>.py
 Core logic: get_<feature>_<action>() functions
 API routes: /api/<feature>/<action> (in app.py)
 Admin dashboard: templates/admin_<feature_name>.html
 Tests: tests/test_<feature_name>.py (15-25 tests)
```

### Key Files
| File | Purpose |
|------|---------|
| `app.py` (7,343L) | Flask routes, webhooks, admin UI, session auth |
| `models.py` (660L) | SQLAlchemy ORM (Order, Payment, Subscription, Customer, etc.) |
| `utils.py` (198L) | `init_db()`, `save_order()`, `mark_order_paid()`, `send_email()`, `get_engine()` |
| `entitlements.py` | Feature flags, rate limiting, download tokens |
| `real_ai_service.py` | Unified AI interface (supports Gemini/OpenAI/Claude/Groq) |
| `executive_dashboard.py` | Aggregates metrics from all 19 features |

### Webhook Idempotency (Critical!)
```python
# In webhook handler:
event_id = extract_entity_id(event) or hash_payload(payload)
if save_webhook(event_id, ...):  # Returns True only on first insert
    process_payment(order_id)     # Only runs once per webhook
```
Razorpay may retry webhooks—this prevents duplicate processing.

### Database Models (Common Query Patterns)
```python
# Get active subscription
sub = session.query(Subscription).filter_by(receipt='cust_123', status='ACTIVE').first()

# Find unpaid orders (24+ hrs old)
cutoff = time.time() - 86400
unpaid = session.query(Order).filter(Order.status == 'created', Order.created_at <= cutoff).all()

# MRR calculation
mrr = session.query(func.sum(Subscription.amount_paise)).filter(
    Subscription.status == 'ACTIVE', 
    Subscription.billing_cycle == 'monthly',
    Subscription.current_period_end > time.time()
).scalar() or 0
```

### Test Pattern
```python
def test_<action>(cleanup_db):  # cleanup_db fixture auto-clears TEST_* records
    result = action_function('TEST_ID_1', {...})
    assert result['id'] == 'TEST_ID_1'
    
# Mock external calls (Razorpay, email)
def test_webhook(client, monkeypatch):
    monkeypatch.setattr(razorpay.WebhookSignature, 'verify', lambda *a, **k: True)
    rv = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'test'})
    assert rv.status_code == 200
```

## Integration Points

| System | Integration | File | Example |
|--------|-----------|------|---------|
| **Razorpay** | Webhooks on `payment.captured` | `app.py` `/webhook` | Signature verification, order marking |
| **Gemini AI** | All 19+ features call unified interface | `real_ai_service.py` | `ai.generate(prompt)` |
| **Email** | Order confirmations, recovery reminders, admin alerts | `utils.py` `send_email()` | SMTP to Outlook |
| **Admin UI** | 48+ dashboards + session auth | `app.py` `/admin/*` | Redirect to `/admin/login` if not authenticated |
| **Stripe** (optional) | Alternative payment provider | `stripe_integration.py` | Independent webhook handler |

## Code Conventions

- **Routes:** `/api/<feature>/<action>` (REST-ish) or `/admin/<feature>` (HTML dashboards)
- **Content negotiation:** `/order/<id>` returns HTML (browser) or JSON (API with Accept header)
- **Feature flags:** `get_flag('feature_name')` → checks `FLAG_FEATURE_NAME` env var
- **Admin protection:** All admin routes check `session.get('admin_logged_in')`; decorator pattern available
- **Error handling:** Flask error handlers (`@app.errorhandler(404)`) + custom exceptions where needed
- **Logging:** Structured logs with `request_id` (via Flask `g`) for tracing across feature engines
- **Email:** Best-effort, non-blocking; uses HTML templates from `templates/email_*.html`

## Environment Variables (Render Dashboard Only — NEVER .env in git)

**Payment:**
- `RAZORPAY_KEY_ID` (rzp_live_...) — LIVE key, NOT test
- `RAZORPAY_KEY_SECRET` — Rotated 1/13/2026
- `RAZORPAY_WEBHOOK_SECRET` — Webhook verification

**AI (Real):**
- `GOOGLE_API_KEY` — Gemini 2.5 Flash (free, 60 req/min)
- `AI_PROVIDER=gemini` — Gemini (not demo mode)

**Email:**
- `EMAIL_USER` — Outlook address
- `EMAIL_PASS` — Outlook app password (NOT regular password!)

**Admin:**
- `ADMIN_USERNAME=admin` (default)
- `ADMIN_PASSWORD` — Session-based login

**Feature Flags:**
- `FLAG_<FEATURE_NAME>=true/false` — Enable/disable features (e.g., `FLAG_RECOMMENDATIONS_ENABLED=true`)

## Adding a New Feature

1. Create `<feature_name>.py` with core functions (`get_<feature>_<action>()`)
2. Add routes to `app.py` following `/api/<feature>/<action>` pattern
3. Create `templates/admin_<feature_name>.html` dashboard
4. Add `tests/test_<feature_name>.py` with 15-25 tests
5. Update `executive_dashboard.py` with `aggregate_<feature>_metrics()` function
6. Document API endpoints in docstrings (auto-populates OpenAPI via `api_documentation.py`)

## Common Debugging Scenarios

### Database Issues
```bash
# Check database location
echo $DATA_DB  # Should be set, defaults to data.db

# Reset database (destructive!)
rm data.db && PYTHONPATH=. alembic upgrade head && python scripts/seed_demo.py seed

# View database schema
sqlite3 data.db ".schema orders"

# Check for locked database
lsof data.db  # See which process is locking it
```

### Payment Webhook Debugging
```python
# Check webhook signature in logs
# Look for "X-Razorpay-Signature" header verification

# Manually trigger webhook test (for dev)
curl -X POST http://localhost:5000/webhook \
  -H "Content-Type: application/json" \
  -H "X-Razorpay-Signature: test_signature" \
  -d '{"event": "payment.captured", "payload": {...}}'

# View recent webhooks
sqlite3 data.db "SELECT id, event, received_at FROM webhooks ORDER BY received_at DESC LIMIT 10"
```

### AI Service Debugging
```python
# Test AI service directly
from real_ai_service import RealAI
ai = RealAI()
result = ai.generate("Test prompt")
print(result)

# Check which provider is active
import os
print(f"Provider: {os.getenv('AI_PROVIDER', 'claude')}")
print(f"Model: {os.getenv('AI_MODEL', 'claude-opus-4.5')}")
```

## Testing Patterns

### Fixture Usage
```python
# cleanup_db fixture auto-removes TEST_* records
def test_feature(cleanup_db):
    result = create_test_order('TEST_ORDER_123')
    assert result['id'] == 'TEST_ORDER_123'
    # Cleanup happens automatically after test
```

### Mocking External Services
```python
def test_payment_webhook(client, monkeypatch):
    # Mock Razorpay signature verification
    monkeypatch.setattr(razorpay.WebhookSignature, 'verify', lambda *a, **k: True)
    
    # Mock email sending
    monkeypatch.setattr('utils.send_email', lambda *a, **k: True)
    
    # Test webhook
    rv = client.post('/webhook', json=payload, headers={'X-Razorpay-Signature': 'test'})
    assert rv.status_code == 200
```

## Security Reminders

 **DO:**
- Store all secrets in Render environment dashboard
- Verify Razorpay webhook signatures using HMAC-SHA256
- Use session-based admin auth (protected routes redirect to `/admin/login`)
- Mock external services in tests (Razorpay, email, AI)

 **DON'T:**
- Commit `.env` with real keys (use Render only)
- Use test Razorpay keys in production (keys rotated 1/13/2026)
- Send unverified webhooks to payment logic
- Hardcode secrets in code or comments

---

**Status: Production LIVE with real payments (Razorpay) + real AI (Gemini 2.5 Flash).** 
