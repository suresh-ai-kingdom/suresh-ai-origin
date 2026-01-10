# Copilot instructions — SURESH AI ORIGIN

Short, actionable guidance to help an AI code agent be productive in this repo.

## Big picture (what this app is)
- Small Flask website that sells and serves product ZIPs from the `downloads/` folder.
- Single module app: `app.py` defines routes, product mapping, and download behavior.
- Templates live in `templates/` (Jinja2), static assets in `static/`.
- Deployment config: `render.yaml` (startCommand: `gunicorn app:app`).

## Key files & what to look for
- `app.py` — core logic. Important bits:
  - `PRODUCTS` dict maps product keys (URLs) to ZIP names. Update both the dict and `downloads/` when adding a product.
  - Routes: `/` (index), `/buy`, `/success`, `/download/<product>` (serves ZIP via `send_from_directory`).
  - **New**: example Razorpay endpoints added: `/create_order` (POST) and `/webhook` (POST). The webhook verifies `X-Razorpay-Signature` with `RAZORPAY_WEBHOOK_SECRET` using `razorpay.WebhookSignature.verify()`.
  - Note: `app.py` now calls `load_dotenv()` so local `.env` files will be loaded in development; in production prefer setting env vars at the host/CI.
- `render.yaml` — deployment on Render: start command uses `gunicorn app:app`.
- `.env` — contains sensitive config (Razorpay keys, email creds, FLASK_SECRET_KEY). **Do not commit secrets.**
- `templates/success.html` — client-side redirect to `/download/{{ product }}` after a 2s delay; changing the download flow must keep this in sync.

## Environment variables (must be set in hosting/CI — DO NOT hardcode)
- RAZORPAY_KEY_ID
- RAZORPAY_KEY_SECRET
- RAZORPAY_WEBHOOK_SECRET
- EMAIL_USER
- EMAIL_PASS
- FLASK_SECRET_KEY
- ADMIN_USERNAME (optional) — when set, enables session-based admin login (see Admin UI)
- ADMIN_PASSWORD (optional) — password used for session-based admin login
- ADMIN_PASSWORD_HASH (optional) — bcrypt-compatible hashed password. If set, it is preferred over `ADMIN_PASSWORD` for verification
- ADMIN_SESSION_TIMEOUT (optional) — session timeout in seconds for admin sessions; if set, admin sessions will be expired after this many seconds of inactivity (default: no timeout)

Session cookie security (recommended for production):
- `SESSION_COOKIE_HTTPONLY` — 'True' or 'False' (default: True)
- `SESSION_COOKIE_SECURE` — 'True' or 'False' (default: True when `FLASK_DEBUG` is not enabled)
- `SESSION_COOKIE_SAMESITE` — 'Lax' | 'Strict' | 'None' (default: 'Lax')

These can be set as environment variables and will be applied at startup; use `apply_session_cookie_config()` in tests after changing env vars.

Security note: In production, ensure `SESSION_COOKIE_SECURE` is `True` and your site is served over HTTPS, set `SESSION_COOKIE_HTTPONLY` to `True` to prevent client-side JS access, and choose an appropriate `SESSION_COOKIE_SAMESITE` policy to match your authentication flow.

The app now logs a **startup warning** if session cookies are configured as insecure (`SESSION_COOKIE_SECURE=false`) while `FLASK_DEBUG` is not enabled — this helps catch unsafe production configurations early.
- ADMIN_TOKEN (optional) — legacy bearer token for API access (still supported)

## Razorpay & webhooks (practical notes)
- `razorpay` is a dependency. If `RAZORPAY_KEY_ID`/`RAZORPAY_KEY_SECRET` are set, a `razorpay.Client` is created.
- The webhook handler in `app.py` verifies `X-Razorpay-Signature` using `RAZORPAY_WEBHOOK_SECRET`.
- Example: to create an order for ₹199, POST `{ "amount": 199 }` to `/create_order` (the server converts to paise automatically).
- Webhook events are now persisted to a local sqlite DB (default `data.db`). The persistence is idempotent (primary key by event id or payload hash).
- Utilities are available in `utils.py`:
  - `save_webhook(event_id, event_name, payload)` — persist an event
  - `get_webhook_by_id(event_id)` — fetch a saved event
  - `send_email(subject, body, to_addr)` — sends email using `EMAIL_USER`/`EMAIL_PASS` (SMTP_SSL) and is safe to monkeypatch in tests
- Tests for persistence and email helper are included in `tests/test_webhook.py` and `tests/test_utils.py`.
- Expand the webhook to record payments/orders in your preferred datastore or add further verification and notification logic as needed.

## Testing
- Basic pytest smoke tests live in `tests/test_app.py` (uses Flask test client).
- Install test deps: `pip install -r requirements.txt` (includes `pytest`).
- Run tests: `pytest -q`.

## Deployment & runtime
- Local debug: `python app.py` (runs Flask; `FLASK_DEBUG` or `.env` controls debug mode).
- Production (as configured): `gunicorn app:app` (matches `render.yaml`). Ensure `gunicorn` is available in your environment (already listed in `requirements.txt`).
- Static files served from `/static`; downloads are served from `downloads/` using `send_from_directory(..., as_attachment=True)`.

## Integration points & gaps to be aware of
- Razorpay is included in `requirements.txt` and example endpoints exist in `app.py`, but business logic for creating orders and marking them fulfilled is intentionally minimal. Implement server-side validation and persistence if you add payments.
- Email settings exist in `.env` but there are no email-sending helpers yet. If adding notifications, use `EMAIL_USER`/`EMAIL_PASS`.

## Project-specific conventions & helpful examples
- Product URL keys are used directly in templates and routes. Example flow:
  - Index links: `/buy?product=starter`
  - Buy page → success page → success page JS redirects to `/download/starter`
  - `app.py` must contain `"starter": "starter_pack.zip"` in `PRODUCTS`.
- When adding a new product, update three places: 1) add ZIP to `downloads/`, 2) add mapping in `PRODUCTS`, and 3) add UI link in `templates/index.html` (or template referenced by UI).

## Debugging tips (repo-specific)
- For quick local testing, run `python app.py` and visit `http://localhost:5000/`.
- Use the browser console to confirm the success-page redirect to `/download/<product>`.
- For production issues, check Gunicorn logs (Render or your host) and ensure environment variables are present.

## Integration test (order → payment → download)
- An integration test `tests/test_integration.py` simulates creating an order via `/create_order`, then posts a `payment.captured` webhook to `/webhook` and asserts the order is marked `paid` and the payment is recorded.
- The test mocks `razorpay_client` and the webhook signature verification so it runs offline and deterministically.
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

## PR checklist for contributors
- [ ] If adding a product: add ZIP to `downloads/` and update `PRODUCTS` & UI templates.
- [ ] If introducing env usage, document required variables and do NOT commit secrets.
- [ ] If using `.env` locally, either load it in `app.py` (we now call `load_dotenv()`) or document that it must be exported.
- [ ] If adding payments: validate webhooks, implement idempotency, and add record persistence.
- [ ] Update `render.yaml` only if the start command or service settings must change.

---

If anything is unclear or you'd like more detail about a particular part (payment integration, email flow, or suggested tests), tell me which area to expand and I’ll iterate. ✅
