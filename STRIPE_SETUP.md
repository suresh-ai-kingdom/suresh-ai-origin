# STRIPE INTEGRATION GUIDE

## Environment Variables (Required for Stripe Phase 2)

### Authentication
```bash
STRIPE_SECRET_KEY=sk_live_xxxxx  # Stripe secret key (from dashboard)
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx  # Stripe publishable key (optional for API, needed for frontend)
STRIPE_WEBHOOK_SECRET=whsec_xxxxx  # Stripe webhook signing secret (from webhook settings)
```

### Pricing (Product Configuration)
```bash
STRIPE_PRICE_PRO=price_1234567890  # Stripe price ID for "pro" tier (~$29/mo)
STRIPE_PRICE_SCALE=price_0987654321  # Stripe price ID for "scale" tier (~$99/mo)
```

### Redirect URLs (Checkout Success/Cancel)
```bash
STRIPE_SUCCESS_URL=https://yourdomain.com/api/billing/success?session_id={CHECKOUT_SESSION_ID}
STRIPE_CANCEL_URL=https://yourdomain.com/api/billing/cancel
```

## Setup Steps

### 1. Create Stripe Account & Products
- Sign up at https://stripe.com
- Create a product (e.g., "SURESH AI ORIGIN Pro")
- Create pricing tiers under the product:
  - Pro: $29/month (annual option available)
  - Scale: $99/month (annual option available)
- Copy the **Price IDs** (starts with `price_`) into env vars

### 2. Configure Webhook
- Go to Stripe Dashboard → Developers → Webhooks
- Add endpoint: `POST https://yourdomain.com/webhook/stripe`
- Select events to receive:
  - `customer.subscription.created`
  - `customer.subscription.updated`
  - `customer.subscription.deleted`
  - `invoice.payment_succeeded`
  - `invoice.payment_failed`
  - `charge.refunded`
- Copy the **Signing Secret** (starts with `whsec_`) into `STRIPE_WEBHOOK_SECRET`

### 3. Set Environment Variables
Add to `.env` or your deployment platform (Render, Heroku, etc.):
```bash
STRIPE_SECRET_KEY=sk_live_xxxxx
STRIPE_PUBLISHABLE_KEY=pk_live_xxxxx
STRIPE_WEBHOOK_SECRET=whsec_xxxxx
STRIPE_PRICE_PRO=price_1234567890
STRIPE_PRICE_SCALE=price_0987654321
```

### 4. Deploy & Test
- Push code to production
- Run migrations: `alembic upgrade head`
- Test checkout flow:
  ```bash
  curl -X POST http://localhost:5000/api/billing/create-checkout \
    -H "Content-Type: application/json" \
    -H "Idempotency-Key: test-123" \
    -d '{
      "receipt": "test_customer_001",
      "tier": "pro",
      "billing_cycle": "month"
    }'
  ```
- Use Stripe test card (4242 4242 4242 4242) to complete checkout

## API Endpoints

### POST `/api/billing/create-checkout`
Create a Stripe Checkout Session.

**Request:**
```json
{
  "receipt": "<customer_id>",
  "tier": "pro" | "scale",
  "billing_cycle": "month" | "year"
}
```

**Response (Success):**
```json
{
  "status": "success",
  "session_id": "cs_live_xxxxx",
  "url": "https://checkout.stripe.com/pay/..."
}
```

### POST `/webhook/stripe`
Receives Stripe webhook events. Handled automatically by the app.

**Signature Verification:**
Uses `X-Stripe-Signature` header and `STRIPE_WEBHOOK_SECRET` to verify authenticity.

**Idempotency:**
Events are stored in `stripe_events` table; processing is idempotent (duplicate events are skipped).

## Integration with Entitlements Layer

The Stripe integration automatically uses the existing `check_entitlement()` layer:
- Before creating checkout, checks if tier is allowed for customer
- Fails with 402 if customer exceeds usage limits or is blocked
- Blocks checkout if `ENFORCE_ENTITLEMENTS=true` and customer violates policy

Example enforcement:
```python
# In create_checkout_session()
entitlement = check_entitlement('checkout', {'tier': tier, 'receipt': receipt})
if entitlement.get('blocked'):
    return {'status': 'error', 'message': '...', 'code': 402}
```

## Database Schema

### Subscriptions Table (Extended)
```sql
CREATE TABLE subscriptions (
  id TEXT PRIMARY KEY,
  receipt TEXT,
  tier TEXT,
  provider TEXT DEFAULT 'razorpay',  -- 'razorpay' or 'stripe'
  stripe_subscription_id TEXT,        -- null if Razorpay
  stripe_customer_id TEXT,            -- null if Razorpay
  razorpay_subscription_id TEXT,      -- null if Stripe
  billing_cycle TEXT,
  amount_paise INTEGER,
  status TEXT,                        -- ACTIVE, PAST_DUE, CANCELLED, TRIAL
  current_period_start FLOAT,
  current_period_end FLOAT,
  created_at FLOAT,
  cancelled_at FLOAT,
  cancellation_reason TEXT
);
```

### Stripe Events Table (New)
```sql
CREATE TABLE stripe_events (
  id TEXT PRIMARY KEY,                -- Stripe event ID
  event_type TEXT,                    -- customer.subscription.created, etc.
  payload TEXT,                       -- Full JSON event
  processed INTEGER DEFAULT 0,        -- 1 = processed, 0 = pending
  processed_at FLOAT,
  received_at FLOAT
);
```

### Usage Meters Table (New)
```sql
CREATE TABLE usage_meters (
  id TEXT PRIMARY KEY,
  receipt TEXT,
  subscription_id TEXT REFERENCES subscriptions(id),
  attribution_runs INTEGER DEFAULT 0,
  models_used INTEGER DEFAULT 0,
  exports INTEGER DEFAULT 0,
  lookback_days INTEGER DEFAULT 7,
  period_start FLOAT,
  period_end FLOAT,
  reset_at FLOAT,
  updated_at FLOAT
);
```

## Testing

### Unit Tests
```bash
pytest tests/test_stripe_integration.py -v
```

### Local Smoke Test
```bash
python stripe_smoke_test.py
```

### Production Monitoring
- Check Stripe Dashboard for failed payments/disputes
- Monitor `/admin/webhooks` for webhook processing errors
- Review alert logs for revenue signals (80/90/100/110% thresholds)

## Troubleshooting

### "Webhook signature verification failed"
- Verify `STRIPE_WEBHOOK_SECRET` matches Dashboard signing secret
- Check webhook endpoint URL is publicly accessible
- Test with Stripe CLI: `stripe listen --forward-to localhost:5000/webhook/stripe`

### "Stripe customer not found in metadata"
- Ensure `create_checkout_session()` successfully creates Stripe customer before checkout
- Check that `receipt` is saved in customer metadata

### "Subscription not created in DB"
- Verify webhook is being received (`/admin/webhooks`)
- Check if event is marked `processed=1` in `stripe_events` table
- Review app logs for exception details

### Testing with Stripe Test Cards
- Success: `4242 4242 4242 4242` any expiry, any CVC
- Decline: `4000 0000 0000 0002` any expiry, any CVC
- 3D Secure: `4000 0025 0000 3155` any expiry, any CVC
- Expired: `4000 0000 0000 0069` any expiry, any CVC

## Coexistence with Razorpay

Both Razorpay and Stripe can coexist:
- Razorpay subscriptions: `provider='razorpay'`, `razorpay_subscription_id` set
- Stripe subscriptions: `provider='stripe'`, `stripe_subscription_id` set
- Entitlements layer checks `provider` when deciding which billing system to use
- Webhooks from both systems are processed independently (different endpoints)

Example customer with both:
```json
{
  "id": "sub_hybrid_001",
  "receipt": "customer_123",
  "tier": "pro",
  "provider": "stripe",  // Currently active via Stripe
  "stripe_subscription_id": "sub_xxxxx",
  "stripe_customer_id": "cus_xxxxx",
  "razorpay_subscription_id": null,
  "status": "ACTIVE"
}
```

## Next Steps

1. **Phase 2.2 (Completed):** Stripe integration endpoints + DB models
2. **Phase 2.3:** Integrate with entitlements for usage-based metering
3. **Phase 3:** Marketing positioning (value prop, pricing page, CTA)
4. **Phase 4:** Tier-aligned AI features (gated by subscription tier)

---

For questions or issues, refer to [Stripe API Docs](https://stripe.com/docs/api) or review the code in `stripe_integration.py`.
