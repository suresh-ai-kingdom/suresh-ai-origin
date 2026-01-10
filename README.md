# SURESH AI ORIGIN

[![CI](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml/badge.svg)](https://github.com/<OWNER>/<REPO>/actions/workflows/ci.yml)

> Tip: Replace `<OWNER>/<REPO>` in the badge URL above with your GitHub repo path (for example `youruser/yourrepo`) to display the workflow status badge for this repository.

Small Flask app that sells and serves product ZIPs from the `downloads/` folder.

Quick start

- Install deps: `pip install -r requirements.txt`
- Run locally: `python app.py`
- Create an order: `POST /create_order` (JSON `{ "amount": 199, "product": "starter" }`)
- Webhook receiver: `POST /webhook` (Razorpay `X-Razorpay-Signature` required when `RAZORPAY_WEBHOOK_SECRET` is set)

Notes

- Replace `<OWNER>/<REPO>` in the CI badge with your GitHub repo path to enable the workflow badge.
- Admin pages: `/admin/webhooks`, `/admin/orders`. You can enable session-based admin login by setting `ADMIN_USERNAME` and `ADMIN_PASSWORD` (this adds `/admin/login` and `/admin/logout`). You can also set `ADMIN_PASSWORD_HASH` to a hashed password (preferred over `ADMIN_PASSWORD` when present). Optionally, set `ADMIN_SESSION_TIMEOUT` (seconds) to automatically expire admin sessions after the given duration. For API/bot access you can still set `ADMIN_TOKEN` to allow Bearer token access.

Security tip: configure secure session cookies in production:
- `SESSION_COOKIE_HTTPONLY=true` (recommended)
- `SESSION_COOKIE_SECURE=true` (requires HTTPS)
- `SESSION_COOKIE_SAMESITE=Lax` (or `Strict` depending on your needs)

Note: the app will log a startup warning if `SESSION_COOKIE_SECURE` is `false` while `FLASK_DEBUG` is not enabled to help catch insecure production configs.

Please follow the PR checklist (see `.github/PULL_REQUEST_TEMPLATE.md`) on all changes that affect security, session cookies, admin auth, or sensitive configuration.
