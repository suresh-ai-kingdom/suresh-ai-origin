# SURESH AI ORIGIN

[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)

> Tip: Replace `<OWNER>/<REPO>` in the badge URL above with your GitHub repo path (for example `youruser/yourrepo`) to display the workflow status badge for this repository.

Small Flask app that sells and serves product ZIPs from the `downloads/` folder.

Quick start

**Automated setup (Windows PowerShell):**
```powershell
.\setup.ps1
```

**Manual setup:**
- Install deps: `pip install -r requirements.txt`
- Apply migrations: `PYTHONPATH=. alembic upgrade head` (PowerShell: `$env:PYTHONPATH='.'; alembic upgrade head`)
- Run locally: `python app.py`
- Create an order: `POST /create_order` (JSON `{ "amount": 199, "product": "starter" }`)
- Webhook receiver: `POST /webhook` (Razorpay `X-Razorpay-Signature` required when `RAZORPAY_WEBHOOK_SECRET` is set)

Database migrations

- Apply latest schema: `PYTHONPATH=. alembic upgrade head` (PowerShell: `$env:PYTHONPATH='.'; alembic upgrade head`).
- SQLite is the default (data.db). Set `DATA_DB` to point to a different DB file if needed.

Demo data

- Use `scripts/seed_demo.py` (requires DB/migrations in place):
	- Seed: `./venv/Scripts/python scripts/seed_demo.py seed`
	- Clear: `./venv/Scripts/python scripts/seed_demo.py clear`
	- Status: `./venv/Scripts/python scripts/seed_demo.py status`

Database backups

- Create backup: `python scripts/backup_db.py create`
- List backups: `python scripts/backup_db.py list`
- Restore backup: `python scripts/backup_db.py restore` (restores most recent, with safety backup)
- Restore specific: `python scripts/backup_db.py restore --backup data_backup_YYYYMMDD_HHMMSS.db`
- Cleanup old backups: `python scripts/backup_db.py cleanup --keep 10`
- Backups stored in `backups/` directory with timestamps

## Customer email notifications

When a payment is captured via Razorpay webhook, the app automatically:
- **Sends professional HTML order confirmation emails** to customers (extracted from payment payload)
- **Includes order details**: order ID, product name, amount paid, download link
- **Sends admin notifications** to `EMAIL_USER` with payment details

Email configuration (required for notifications):
- `EMAIL_USER=your-email@gmail.com`
- `EMAIL_PASS=your-app-password` (use Gmail App Password, not regular password)

The HTML email template ([templates/email_order_confirmation.html](templates/email_order_confirmation.html)) features:
- Responsive design with gradient header
- Order summary table
- One-click download button
- Professional footer with branding

Email sending is best-effort and will not block webhook processing if it fails.

## Customer order tracking page

Customers can track their orders **without admin access** by visiting:
```
GET /order/<order_id>
```

The tracking page displays:
- **Order ID** - Unique identifier for the purchase
- **Product name** - What was purchased
- **Amount paid** - Purchase price in rupees
- **Payment status** - Shows "Paid" or "Awaiting Payment"
- **Download link** - One-click download for paid orders

### Smart content negotiation:
- **Browser requests** (HTML) → Beautiful tracking page with download button
- **API requests** (JSON Accept header) → JSON response with order details

### Example URLs:
- Customer tracking: `https://yoursite.com/order/order_abc123`
- API call: `curl -H "Accept: application/json" https://yoursite.com/order/order_abc123`

Unpaid orders show a status message reminding customers to complete payment. Download buttons are disabled until payment is confirmed.

- `SESSION_COOKIE_SECURE=true` (requires HTTPS)
- `SESSION_COOKIE_SAMESITE=Lax` (or `Strict` depending on your needs)

Note: the app will log a startup warning if `SESSION_COOKIE_SECURE` is `false` while `FLASK_DEBUG` is not enabled to help catch insecure production configs.

Please follow the PR checklist (see `.github/PULL_REQUEST_TEMPLATE.md`) on all changes that affect security, session cookies, admin auth, or sensitive configuration.

## Stripe Integration (Phase 2)

**Status:** ✅ Live and ready for production deployment

The app now supports Stripe subscriptions alongside Razorpay. Key files:

- **[STRIPE_SETUP.md](STRIPE_SETUP.md)** — Environment variables, webhook configuration, API endpoint docs, troubleshooting
- **stripe_integration.py** — Checkout sessions, webhook handling, idempotent event processing, subscription state management
- **models.py** — Subscription (extended with Stripe fields), StripeEvent, UsageMeter tables

### Quick Start (Stripe)

1. **Get Stripe credentials** from your Stripe Dashboard (API keys, webhook signing secret)
2. **Set environment variables** (see [STRIPE_SETUP.md](STRIPE_SETUP.md))
3. **Deploy migration:** `alembic upgrade head`
4. **Test checkout:** `POST /api/billing/create-checkout` (see endpoint docs)
5. **Verify webhook:** Configure webhook in Stripe Dashboard → Developers → Webhooks

Both Razorpay and Stripe subscriptions coexist in the same database (provider field).

## Marketing & Positioning

See **[MARKETING_POSITIONING.md](MARKETING_POSITIONING.md)** for:
- Product positioning (problem, solution, differentiators)
- 3 buyer personas and their win scenarios
- Pricing tiers (Starter free, Pro $29, Scale $99)
- 30-day growth targets and go-to-market strategy
- Messaging examples and success metrics

