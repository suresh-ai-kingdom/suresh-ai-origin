# Make.com & Zapier Integration Guide

## Overview

SURESH AI ORIGIN provides webhook endpoints for no-code automation via Make.com and Zapier.

**Available Endpoints:**
- `POST /hooks/make` - Make.com incoming webhook
- `POST /hooks/zapier` - Zapier incoming webhook

Both endpoints support optional signature verification via the `X-Webhook-Secret` header.

---

## Setup

### 1. Set Webhook Secret (Optional but Recommended)

In your Render dashboard, add an environment variable:

```
WEBHOOK_SHARED_SECRET=your_secret_key_here
```

### 2. Make.com Integration

**Step 1: Create Module**
1. Go to Make.com → Create scenario
2. Add "HTTP" module → "Make a request"
3. Set method to `POST`
4. URL: `https://sureshaiorigin.com/hooks/make`

**Step 2: Configure Payload**

```json
{
  "event": "trial_created",
  "user_email": "user@example.com",
  "plan": "pro",
  "created_at": "2026-01-18T12:00:00Z"
}
```

**Step 3: Add Header (if using secret)**

```
Header: X-Webhook-Secret
Value: your_secret_key_here
```

**Step 4: Add to Trigger**

Example: When a new row is added to a sheet:
- Trigger: Google Sheets → New Row
- Action: HTTP → Make request to `/hooks/make`
- Payload includes row data (email, plan, etc.)

---

### 3. Zapier Integration

**Step 1: Create Zap**
1. Go to Zapier → Create → Zap
2. Trigger: Your source app (Gmail, Slack, Form, etc.)
3. Action: Webhooks by Zapier → "Catch Raw Hook" (outgoing)

**Step 2: Get Hook URL**

Zapier will give you a temporary URL. Map it to your Make.com endpoint:
```
https://sureshaiorigin.com/hooks/zapier
```

**Step 3: Send Payload**

Configure your trigger to POST JSON to the endpoint:

```json
{
  "event": "customer_signup",
  "name": "John Doe",
  "email": "john@example.com",
  "source": "zapier"
}
```

**Step 4: Test & Deploy**

- Test the zap
- Click "Deploy"

---

## Example Payloads

### Trial Signup

```json
{
  "event": "trial_created",
  "user_id": "user_123",
  "email": "test@example.com",
  "name": "Test User",
  "plan": "pro",
  "trial_days": 14,
  "created_at": "2026-01-18T10:30:00Z"
}
```

### Feature Usage

```json
{
  "event": "rare_feature_used",
  "feature": "rare_destiny",
  "user_id": "user_456",
  "payload_size": 1024,
  "latency_ms": 250,
  "success": true,
  "created_at": "2026-01-18T10:31:00Z"
}
```

### Payment

```json
{
  "event": "payment_received",
  "order_id": "order_789",
  "amount_paise": 499900,
  "customer_email": "cust@example.com",
  "plan": "lifetime",
  "created_at": "2026-01-18T10:32:00Z"
}
```

---

## Response

All webhooks return:

```json
{
  "success": true
}
```

With HTTP 200 on success, 403 on auth failure, 400 on invalid data.

---

## Logging & Monitoring

All webhook events are logged to `data/webhooks.jsonl` with:
- Timestamp
- Source (make.com or zapier)
- Request headers
- Request body
- Response status

Monitor via:
```bash
tail -f data/webhooks.jsonl | jq .
```

---

## Use Cases

### 1. Auto-Send Welcome Email on Trial Signup

**Make.com Flow:**
- Trigger: POST /hooks/make with `event: trial_created`
- Action: Gmail → Send email with trial credentials

### 2. Log Feature Usage to Analytics Sheet

**Zapier Flow:**
- Trigger: Any source triggers feature usage
- Action: Google Sheets → Append row with feature usage
- POST to `/hooks/zapier` with event data

### 3. Slack Alerts on High-Value Customer Signup

**Make.com Flow:**
- Trigger: Custom webhook with customer data
- Action: Slack → Send message to #sales channel

---

## Troubleshooting

### 403 Forbidden
- Check `WEBHOOK_SHARED_SECRET` env var is set and matches header
- If not using auth, remove the secret from Make/Zapier

### Webhook Not Received
- Check Render logs: `tail -f data/webhooks.jsonl`
- Verify endpoint URL is correct
- Test with curl:

```bash
curl -X POST https://sureshaiorigin.com/hooks/make \
  -H "Content-Type: application/json" \
  -d '{"event": "test", "data": "test"}'
```

### Timeout (504)
- Webhook processing takes time; Render default timeout is 30s
- If payload is very large, split into smaller requests

---

## Security Notes

1. **Always use `WEBHOOK_SHARED_SECRET`** in production
2. **Validate webhook IP** (advanced): Whitelist Make/Zapier IPs in firewall
3. **Rate limit** (optional): Add `limit_make=100/min` env var
4. **Log everything**: All requests logged to `data/webhooks.jsonl`

---

## Support

For issues:
1. Check `data/webhooks.jsonl` for payload and error details
2. Check `data/health_log.jsonl` for endpoint health
3. Render Logs: Dashboard → Logs

---

**Last Updated:** Jan 18, 2026  
**Platform:** SURESH AI ORIGIN v2.7
