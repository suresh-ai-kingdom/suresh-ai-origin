## Summary

Please include a summary of the changes and the related issue (if any).

## Checklist
- [ ] I have added tests that cover my changes (if applicable).
- [ ] I have run the full test suite locally (`pytest -q`) and all tests pass.
- [ ] I have updated documentation where necessary (README / .github/copilot-instructions.md).

## Security / Production Readiness
- [ ] Confirm `SESSION_COOKIE_SECURE` is `true` when `FLASK_DEBUG` is not enabled (production), or explain why an exception is required.
- [ ] Confirm `SESSION_COOKIE_HTTPONLY` is `true` in production to prevent client-side JS access to session cookies.
- [ ] If adding or changing admin auth/credentials, confirm `ADMIN_USERNAME`, `ADMIN_PASSWORD_HASH` (preferred), and `ADMIN_SESSION_TIMEOUT` are set appropriately and documented.
- [ ] For sensitive changes (payments, webhooks, secrets), confirm environment variables are **NOT** committed and are documented in `.env.example` or deployment docs.

## Notes
- Include any deployment or migration notes here.
