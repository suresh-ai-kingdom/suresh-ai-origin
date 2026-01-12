# Billing & Plan Management

## Architecture: Stripe-First with Razorpay Extension

### Core Design Principles
- **Stripe is the primary billing provider** for global customers
- Razorpay is an optional regional extension for India/Asia markets
- Plan enforcement happens at the application layer, not payment layer
- Usage metering is centralized and provider-agnostic

---

## Plan Tiers

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

---

## Environment Configuration

### Required for Production
```bash
# Plan tier (controls feature access)
PLAN_TIER=pro  # free|pro|scale

# Stripe (primary billing)
STRIPE_SECRET_KEY=sk_live_...
STRIPE_PUBLISHABLE_KEY=pk_live_...
STRIPE_WEBHOOK_SECRET=whsec_...

# Price IDs for each tier
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_SCALE=price_...
```

### Optional (Razorpay for regional markets)
```bash
RAZORPAY_KEY_ID=rzp_live_...
RAZORPAY_KEY_SECRET=...
RAZORPAY_WEBHOOK_SECRET=...
```

---

## Usage Tracking

### Current Implementation
Plan usage is exposed via helper functions in `app.py`:

```python
def get_current_plan() -> str:
    """Returns 'free', 'pro', or 'scale' based on PLAN_TIER env var"""
    
def get_plan_limits(plan: str | None = None) -> dict:
    """Returns limits dict for given plan tier"""
    
def get_plan_usage_snapshot() -> dict:
    """Returns current usage counters for metering"""
```

### Next Steps for Production
1. **Wire usage counters to real DB**
   - Track `attribution_runs` in database per customer
   - Increment on each `/api/attribution/track-journey` call
   - Reset monthly based on billing cycle

2. **Add middleware for limit enforcement**
   - Check usage before allowing API calls
   - Return 429 + upgrade CTA when limits exceeded

3. **Implement Stripe metered billing**
   - Report usage to Stripe via `/v1/subscription_items/.../usage_records`
   - Use Stripe's usage-based pricing for scale tier

---

## Billing Flow (Stripe-First)

### 1. Customer Signs Up
- Create Stripe customer: `POST /v1/customers`
- Store `stripe_customer_id` in database
- Assign default plan: `free`

### 2. Customer Upgrades
- **UI**: User clicks "Upgrade to Scale" button in attribution dashboard
- **Backend**: Redirect to Stripe Checkout
  ```python
  stripe.checkout.Session.create(
      customer=stripe_customer_id,
      line_items=[{"price": STRIPE_PRICE_ID_SCALE, "quantity": 1}],
      mode="subscription",
      success_url="/billing/success",
      cancel_url="/admin/pricing"
  )
  ```

### 3. Webhook Processing
- Stripe sends `checkout.session.completed` → update `PLAN_TIER` in DB
- Stripe sends `customer.subscription.deleted` → downgrade to `free`
- Store subscription ID for future management

### 4. Plan Enforcement
- All admin routes check `get_current_plan()` and compare to required tier
- API endpoints validate usage via `get_plan_usage_snapshot()`
- UI displays upgrade CTA when limits approaching

---

## Razorpay Extension (Optional)

### When to Use
- Customer's billing address is in India
- Customer prefers UPI/Netbanking/local payment methods
- Same subscription tiers, just different payment processor

### Implementation
```python
# In app.py
BILLING_PROVIDER = os.getenv('BILLING_PROVIDER', 'stripe')  # stripe|razorpay

if BILLING_PROVIDER == 'razorpay' and RAZORPAY_KEY_ID:
    razorpay_client = razorpay.Client(auth=(RAZORPAY_KEY_ID, RAZORPAY_KEY_SECRET))
```

### Razorpay Checkout Flow
```python
# Create subscription
razorpay_client.subscription.create({
    "plan_id": RAZORPAY_PLAN_ID_SCALE,
    "customer_notify": 1,
    "total_count": 12,  # 12 months
    "notes": {"plan_tier": "scale"}
})
```

---

## Security Checklist

✅ **Webhook Signature Verification**
- Stripe: `stripe.Webhook.construct_event()` with `STRIPE_WEBHOOK_SECRET`
- Razorpay: `razorpay.WebhookSignature.verify()` with `RAZORPAY_WEBHOOK_SECRET`

✅ **Idempotency**
- Store webhook `event_id` in database to prevent duplicate processing
- Existing implementation in `utils.py`: `save_webhook(event_id, ...)`

✅ **Plan Downgrade Protection**
- Don't delete data when downgrading
- Lock export/advanced features but preserve historical data
- Grace period before hard limits enforced

✅ **Subscription Status Sync**
- Query Stripe API on app startup to sync subscription state
- Handle edge cases: payment failed, subscription paused, etc.

---

## Testing

### Stripe Test Mode
```bash
STRIPE_SECRET_KEY=sk_test_...
STRIPE_PUBLISHABLE_KEY=pk_test_...
STRIPE_WEBHOOK_SECRET=whsec_... (from Stripe CLI)
```

Use Stripe CLI for webhook testing:
```bash
stripe listen --forward-to localhost:5000/webhook/stripe
stripe trigger checkout.session.completed
```

### Razorpay Test Mode
```bash
RAZORPAY_KEY_ID=rzp_test_...
RAZORPAY_KEY_SECRET=...
```

---

## Migration Path

### Phase 1: Current State ✅
- Plan context exposed in backend (`get_current_plan`, `get_plan_limits`)
- UI shows plan badge, usage meter, upgrade CTA
- Manual plan assignment via `PLAN_TIER` env var

### Phase 2: Stripe Integration (Next)
- Add Stripe SDK to `requirements.txt`
- Create `/api/billing/create-checkout` endpoint
- Implement webhook handler at `/webhook/stripe`
- Store `stripe_customer_id` and `stripe_subscription_id` in DB

### Phase 3: Usage Enforcement
- Add usage tracking middleware
- Increment counters in DB on API calls
- Return 402 Payment Required when limits exceeded
- Report usage to Stripe for metered billing

### Phase 4: Razorpay Extension (Optional)
- Duplicate Stripe flow for Razorpay
- Route customers based on geography or preference
- Unified subscription management in admin panel

---

## Database Schema (Recommended)

```sql
CREATE TABLE subscriptions (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    provider VARCHAR(50) NOT NULL,  -- 'stripe' or 'razorpay'
    external_customer_id VARCHAR(255),  -- stripe_customer_id or razorpay_customer_id
    external_subscription_id VARCHAR(255),
    plan_tier VARCHAR(50) NOT NULL,  -- 'free', 'pro', 'scale'
    status VARCHAR(50),  -- 'active', 'past_due', 'canceled'
    current_period_end TIMESTAMP,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE usage_metrics (
    id SERIAL PRIMARY KEY,
    customer_id VARCHAR(255) NOT NULL,
    metric_name VARCHAR(100),  -- 'attribution_runs', 'models_trained', etc.
    value INTEGER DEFAULT 0,
    period_start TIMESTAMP,
    period_end TIMESTAMP,
    reported_to_provider BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_usage_customer_period ON usage_metrics(customer_id, period_start, period_end);
CREATE INDEX idx_subscriptions_customer ON subscriptions(customer_id);
```

---

## Revenue Optimization

### Pricing Strategy
- **Free**: Marketing funnel, capture leads, low-cost high-volume
- **Pro**: $49/month - Primary revenue driver, targets SMBs
- **Scale**: $199/month - High-value customers, metered overage charges

### Upsell Triggers
- Show upgrade CTA when user hits 80% of free tier limits
- Email notification at 90% usage
- Soft limit at 100% with 7-day grace period
- Hard limit at 110% with payment required

### Metrics to Track
- Conversion rate: Free → Pro → Scale
- Churn rate per tier
- Average revenue per user (ARPU)
- Lifetime value (LTV) by acquisition channel

---

## Support Contacts

- **Stripe**: https://support.stripe.com | [email protected]
- **Razorpay**: https://razorpay.com/support/ | [email protected]

---

**Last Updated**: January 12, 2026
**Owner**: Platform Engineering Team
**Status**: Phase 1 Complete, Stripe Integration Next
