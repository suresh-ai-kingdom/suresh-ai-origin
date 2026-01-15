# SAi Robots Product Spec
**Purpose:** Define digital robots lineup, capabilities, licensing, and provisioning for Suresh AI Origin.

## 1) Product Line (Robots-as-Software)
- SAi-v1 Core Ops: Task automation, data entry, email triage, webhook handling.
- SAi-v2 Support Desk: Ticket triage, canned responses, SLA alerts, CSAT surveys.
- SAi-v3 Sales Scout: Lead scrape/enrich, outreach sequences, meeting booking.
- SAi-v4 Finance Buddy: Invoices, payouts, EMI schedules, reconciliation drafts.
- SAi-v5 Marketing Pilot: Campaign drafts, ad variants, A/B setup, social posting.
- SAi-v6 Analytics Pro: Dashboards, anomaly alerts, cohort/retention insights.
- SAi-v7 Security Sentry: Access audits, secret rotation reminders, webhook tamper checks.
- SAi-v8 DevOps Ghost: Health checks, log scanning, error routing, rollback suggestions.
- SAi-v9 Industry Specialist: Pluggable skills per vertical (SaaS, D2C, Healthcare, BFSI).

## 2) Personas & Naming
- Each version can be personalized with a human codename (e.g., SAi-v3 "Arjun" for sales, SAi-v6 "Meera" for analytics).
- SKU remains SAi-vN for billing and license tracking.

## 3) Capabilities Model
- Skills: Modular skill packs (Outreach, Reconcile, A/B Test, Webhook Guard, Churn Watch, etc.).
- Context adapters: CRM, ERP, Helpdesk, Ads, Razorpay/Stripe, Email (SMTP/IMAP), Slack/Teams, Webhooks.
- Guardrails: Role-based scopes, rate limits, approval steps, audit logs, dry-run mode.

## 4) Licensing & Commercial Models
- Access modes:
  1) Subscription (monthly/annual; per-robot or bundle)
  2) Rental (weekly burst)
  3) EMI-to-Own (converts to perpetual after term)
  4) Perpetual + AMC (one-time + annual care)
- Tiers:
  - Starter: 1 robot, limited skills, capped runs/month.
  - Growth: 3 robots, more skills, higher caps, email+webhook integrations.
  - Scale: 5-10 robots, all skills, SSO, custom SLAs, audit exports.
  - Enterprise: Unlimited robots, custom skills, private models, VPC, priority SRE.
- Billing add-ons: Extra skill packs, extra run-quota, premium support (24/7), dedicated success engineer.
- Compliance: DPA/SLA per tier; audit log retention by tier.

## 5) Ownership & EMI Flow
- EMI: 6/9/12-month plans; converts to perpetual license at completion; AMC optional.
- Ownership proof: License certificate with robot ID (SAi-vN-UUID), scope, expiration (if any).
- Transfer: Allow license transfer with a reissue fee; track chain-of-custody.
- Checkout data: Org name, billing contact, technical contact, intended systems (CRM/ERP/etc), data residency preference.

## 6) Technical Delivery
- Provisioning: Issue a robot token (scoped JWT) + config file (skills enabled, rate limits, webhooks).
- Deployment: Runs as background service; jobs triggered by webhooks/cron/API.
- Observability: Per-robot dashboard—runs, success/fail, approvals, spend, ROI.
- Safety: Dry-run mode, approval steps for money-moving actions, HMAC for incoming webhooks, signed callbacks.

## 7) Operational Playbook
- Intake: Pick versions, choose skills, choose tier, select access mode (sub/rent/EMI/perpetual), sign SLA/DPA.
- Provision: Generate robot IDs, tokens, config; enable skills; set limits; connect integrations.
- Handoff: Provide admin dashboard access; run test flows; enable alerts to Slack/Email.
- Run: Monitor jobs; iterate skills; add/remove packs.
- Review: Monthly ROI review; upsell skill packs; adjust quotas.

## 8) Pricing Skeleton (Illustrative)
- Starter: 4,999/mo per robot (core skills, capped runs)
- Growth: 14,999/mo (3 robots bundle)
- Scale: 39,999/mo (5 robots + all skill packs)
- Enterprise: Custom (unlimited, private deployment, SRE)
- EMI-to-own: 12x monthly at ~1.2x perpetual list, then perpetual + optional AMC (15-20%/yr)

## 9) Data Model (High Level)
- Robot: id, version, persona_name, tier, skills[], limits, status.
- License: id, robot_id, mode (sub/rent/emi/perpetual), start_at, end_at, emi_terms, transfer_allowed.
- BillingPlan: id, price, currency, cadence, add_ons[].
- RunLog: robot_id, job_id, input_ref, output_ref, status, duration_ms, cost_estimate.
- Audit: actor, action, before/after, timestamp, signature.

## 10) Checkout Steps
1) Select versions + skill packs.
2) Choose tier + access mode (sub/rent/EMI/perpetual).
3) Provide systems to integrate (CRM/ERP/Helpdesk/Ads/Payment).
4) Sign SLA/DPA; choose data residency.
5) Pay (Razorpay/Stripe)  provision robot token + config.
6) Run guided test flow; enable alerts; go live.

## 11) API/Provisioning Stubs (outline)
- POST /api/robots -> create robot (version, persona, skills, tier, limits)
- POST /api/robots/{id}/license -> create license (mode, term, emi_plan)
- POST /api/robots/{id}/token -> issue scoped token (roles, quotas)
- POST /api/robots/{id}/skills -> enable/disable skill packs
- POST /api/robots/{id}/webhooks -> register inbound/outbound hooks (with HMAC secret)
- GET /api/robots/{id}/runs -> list runs, status, cost_estimate
- POST /api/robots/{id}/run -> trigger job (with dry-run flag)

## 12) Safety & Compliance
- Role-scoped tokens; least privilege by default.
- All money-moving actions require approvals or dry-run first.
- HMAC verify all inbound webhooks; sign outbound callbacks.
- Per-tenant encryption at rest; redact PII in logs where possible.
- Audit trails for all actions; exportable for enterprise tiers.

## 13) Success Criteria
- Time-to-first-robot: < 10 minutes from checkout to live token.
- First successful run: < 30 minutes with guided test flow.
- ROI visibility: Dashboard shows runs, time saved, revenue impact.
- Upsell path: Skill packs and higher tiers visible in admin.

## 14) Next Steps
- Wire into existing checkout flow (Razorpay) with new products/SKUs.
- Add robot provisioning endpoints + admin UI for robots/licenses/skills.
- Add dashboard cards for runs, approvals, ROI, spend.
- Prepare marketing copy per SAi-vN persona for social/ads.

---
**Owner:** Suresh AI Origin
**Status:** Draft ready for implementation
