# Stripe Billing Integration

## Quick Start (Stripe-First Architecture)

### 1. Install Stripe SDK
```bash
pip install stripe>=8.0.0
```

### 2. Set Environment Variables
```bash
# Required for Stripe billing
STRIPE_SECRET_KEY=sk_test_...  # Use sk_live_... in production
STRIPE_PUBLISHABLE_KEY=pk_test_...  # Use pk_live_... in production  
STRIPE_WEBHOOK_SECRET=whsec_...  # From Stripe Dashboard or CLI

# Price IDs for each plan tier (create in Stripe Dashboard)
STRIPE_PRICE_ID_PRO=price_...
STRIPE_PRICE_ID_SCALE=price_...

# Customer plan tier (set after subscription creation)
PLAN_TIER=pro  # or 'free', 'scale'
```

### 3. Create Stripe Products & Prices

In Stripe Dashboard (https://dashboard.stripe.com/test/products):

**Product: Pro Plan**
- Name: "Attribution Analytics Pro"
- Description: "5,000 monthly attribution runs, 3 models, 60-day lookback"
- Recurring: Monthly
- Price: $49/month
- Copy Price ID → Set as `STRIPE_PRICE_ID_PRO`

**Product: Scale Plan**
- Name: "Attribution Analytics Scale"
- Description: "25,000 monthly attribution runs, 10 models, 180-day lookback, exports enabled"
- Recurring: Monthly
- Price: $199/month  
- Copy Price ID → Set as `STRIPE_PRICE_ID_SCALE`

---

## Implementation Roadmap

### Phase 1: Checkout Flow (NEXT)

**Backend Route: Create Checkout Session**
```python
@app.route('/api/billing/create-checkout', methods=['POST'])
@admin_required
def create_stripe_checkout():
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    data = request.get_json()
    plan_tier = data.get('plan_tier')  # 'pro' or 'scale'
    
    # Map plan tier to Stripe price ID
    price_ids = {
        'pro': os.getenv('STRIPE_PRICE_ID_PRO'),
        'scale': os.getenv('STRIPE_PRICE_ID_SCALE'),
    }
    
    price_id = price_ids.get(plan_tier)
    if not price_id:
        return jsonify({'error': 'Invalid plan tier'}), 400
    
    # Get or create Stripe customer
    customer_id = session.get('stripe_customer_id')
    if not customer_id:
        customer = stripe.Customer.create(
            email=session.get('admin_username'),  # or user email
            metadata={'internal_user_id': session.get('admin_username')}
        )
        customer_id = customer.id
        # Store in session or DB
        session['stripe_customer_id'] = customer_id
    
    # Create Checkout session
    checkout_session = stripe.checkout.Session.create(
        customer=customer_id,
        line_items=[{
            'price': price_id,
            'quantity': 1,
        }],
        mode='subscription',
        success_url=url_for('billing_success', _external=True) + '?session_id={CHECKOUT_SESSION_ID}',
        cancel_url=url_for('admin_attribution', _external=True),
        metadata={'plan_tier': plan_tier}
    )
    
    return jsonify({
        'checkout_url': checkout_session.url,
        'session_id': checkout_session.id
    }), 200
```

**Frontend: Upgrade Button Click**
```javascript
// In admin_attribution.html - modify upgrade button
document.querySelector('.btn-upgrade').addEventListener('click', function(e) {
    e.preventDefault();
    const planTier = this.dataset.tier || 'scale';
    
    fetch('/api/billing/create-checkout', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({plan_tier: planTier})
    })
    .then(r => r.json())
    .then(data => {
        if (data.checkout_url) {
            window.location.href = data.checkout_url;  // Redirect to Stripe Checkout
        }
    });
});
```

---

### Phase 2: Webhook Handler

**Endpoint: Handle Stripe Webhooks**
```python
@app.route('/webhook/stripe', methods=['POST'])
def stripe_webhook():
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    payload = request.data
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except Exception as e:
        logging.error(f"Stripe webhook signature verification failed: {e}")
        return ('Invalid signature', 400)
    
    # Handle event types
    if event['type'] == 'checkout.session.completed':
        session_obj = event['data']['object']
        customer_id = session_obj['customer']
        subscription_id = session_obj['subscription']
        plan_tier = session_obj['metadata'].get('plan_tier', 'pro')
        
        # Store subscription in database
        from utils import save_webhook
        from models import get_session, Subscriptions
        
        save_webhook(event['id'], event['type'], payload.decode('utf-8'))
        
        db_session = get_session()
        subscription = Subscriptions(
            customer_id=customer_id,
            provider='stripe',
            external_subscription_id=subscription_id,
            plan_tier=plan_tier,
            status='active'
        )
        db_session.add(subscription)
        db_session.commit()
        
        logging.info(f"Subscription created: {subscription_id} for customer {customer_id}, tier {plan_tier}")
    
    elif event['type'] == 'customer.subscription.updated':
        subscription_obj = event['data']['object']
        subscription_id = subscription_obj['id']
        status = subscription_obj['status']
        
        # Update subscription status in DB
        db_session = get_session()
        subscription = db_session.query(Subscriptions).filter_by(
            external_subscription_id=subscription_id
        ).first()
        if subscription:
            subscription.status = status
            db_session.commit()
            logging.info(f"Subscription {subscription_id} updated to {status}")
    
    elif event['type'] == 'customer.subscription.deleted':
        subscription_obj = event['data']['object']
        subscription_id = subscription_obj['id']
        
        # Downgrade to free tier
        db_session = get_session()
        subscription = db_session.query(Subscriptions).filter_by(
            external_subscription_id=subscription_id
        ).first()
        if subscription:
            subscription.status = 'canceled'
            subscription.plan_tier = 'free'
            db_session.commit()
            logging.info(f"Subscription {subscription_id} canceled, downgraded to free")
    
    return ('Success', 200)
```

**Test Webhooks Locally**
```bash
# Install Stripe CLI
stripe login

# Forward webhooks to local dev server
stripe listen --forward-to localhost:5000/webhook/stripe

# Trigger test events
stripe trigger checkout.session.completed
stripe trigger customer.subscription.deleted
```

---

### Phase 3: Plan Enforcement Middleware

**Usage Tracking**
```python
# In app.py - add before attribution routes

def check_plan_limits(feature='attribution_runs'):
    """Middleware to enforce plan limits on API calls."""
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            plan_tier = get_current_plan()
            limits = get_plan_limits(plan_tier)
            usage = get_plan_usage_snapshot()
            
            if feature == 'attribution_runs':
                if usage['attribution_runs'] >= limits['attribution_runs']:
                    return jsonify({
                        'error': 'Plan limit exceeded',
                        'message': f'You have used {usage["attribution_runs"]}/{limits["attribution_runs"]} attribution runs this month.',
                        'upgrade_url': url_for('admin_pricing'),
                        'current_plan': plan_tier
                    }), 402  # 402 Payment Required
            
            return func(*args, **kwargs)
        return wrapper
    return decorator

# Apply to attribution tracking route
@app.route('/api/attribution/track-journey', methods=['POST'])
@admin_required
@check_plan_limits('attribution_runs')
def api_attribution_track_journey():
    # ... existing code ...
    
    # Increment usage counter after successful tracking
    increment_usage_counter('attribution_runs')
    
    return jsonify({'success': True, 'attribution': result}), 201
```

**Helper: Increment Usage**
```python
def increment_usage_counter(metric_name='attribution_runs'):
    """Increment usage counter for current billing period."""
    from models import get_session, UsageMetrics
    from datetime import datetime
    
    customer_id = session.get('stripe_customer_id') or session.get('admin_username', 'anonymous')
    
    # Get current billing period (monthly reset)
    now = datetime.utcnow()
    period_start = datetime(now.year, now.month, 1)
    
    db_session = get_session()
    usage = db_session.query(UsageMetrics).filter_by(
        customer_id=customer_id,
        metric_name=metric_name,
        period_start=period_start
    ).first()
    
    if usage:
        usage.value += 1
    else:
        usage = UsageMetrics(
            customer_id=customer_id,
            metric_name=metric_name,
            value=1,
            period_start=period_start,
            period_end=datetime(now.year, now.month + 1, 1) if now.month < 12 else datetime(now.year + 1, 1, 1)
        )
        db_session.add(usage)
    
    db_session.commit()
```

---

### Phase 4: Customer Portal (Self-Service)

**Stripe Customer Portal Integration**
```python
@app.route('/api/billing/portal', methods=['POST'])
@admin_required
def create_portal_session():
    import stripe
    stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
    
    customer_id = session.get('stripe_customer_id')
    if not customer_id:
        return jsonify({'error': 'No active subscription'}), 400
    
    # Create portal session
    portal_session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=url_for('admin_attribution', _external=True),
    )
    
    return jsonify({'portal_url': portal_session.url}), 200
```

**Frontend: "Manage Billing" Button**
```javascript
// Add to plan banner in admin_attribution.html
<button class="btn-secondary" onclick="manageBilling()">Manage Billing</button>

<script>
function manageBilling() {
    fetch('/api/billing/portal', {method: 'POST'})
        .then(r => r.json())
        .then(data => {
            if (data.portal_url) {
                window.location.href = data.portal_url;
            }
        });
}
</script>
```

---

## Database Models (Add to models.py)

```python
class Subscriptions(Base):
    __tablename__ = 'subscriptions'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(255), nullable=False, index=True)
    provider = Column(String(50), nullable=False)  # 'stripe' or 'razorpay'
    external_customer_id = Column(String(255))
    external_subscription_id = Column(String(255), unique=True)
    plan_tier = Column(String(50), nullable=False)  # 'free', 'pro', 'scale'
    status = Column(String(50))  # 'active', 'past_due', 'canceled', 'incomplete'
    current_period_end = Column(DateTime)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    updated_at = Column(DateTime, default=lambda: datetime.utcnow(), onupdate=lambda: datetime.utcnow())


class UsageMetrics(Base):
    __tablename__ = 'usage_metrics'
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(String(255), nullable=False, index=True)
    metric_name = Column(String(100), nullable=False)  # 'attribution_runs', 'models', etc.
    value = Column(Integer, default=0)
    period_start = Column(DateTime, nullable=False)
    period_end = Column(DateTime)
    reported_to_provider = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.utcnow())
    
    __table_args__ = (
        Index('idx_usage_customer_period', 'customer_id', 'metric_name', 'period_start'),
    )
```

---

## Testing Checklist

✅ **Local Development**
- [ ] Stripe SDK installed: `pip install stripe>=8.0.0`
- [ ] Test keys configured in `.env`
- [ ] Stripe CLI listening: `stripe listen --forward-to localhost:5000/webhook/stripe`
- [ ] Test checkout: Click upgrade button, complete payment with test card `4242 4242 4242 4242`
- [ ] Verify webhook received and subscription created in DB

✅ **Plan Enforcement**
- [ ] Free tier shows upgrade CTA when limits approached
- [ ] API returns 402 when limits exceeded
- [ ] Usage counter increments correctly
- [ ] Monthly reset works (test by manually updating period_start)

✅ **Security**
- [ ] Webhook signature verification enabled
- [ ] Customer email validation before creating Stripe customer
- [ ] Subscription status synced from webhooks, not client input
- [ ] Admin routes protected with `@admin_required`

---

## Go-Live Checklist

🚀 **Pre-Production**
- [ ] Replace test keys with live keys: `sk_live_...`, `pk_live_...`
- [ ] Create live products & prices in Stripe Dashboard
- [ ] Configure webhook endpoint in Stripe: `https://yourdomain.com/webhook/stripe`
- [ ] Test end-to-end flow in production-like environment
- [ ] Set up Stripe webhook endpoint monitoring (Stripe sends alerts for failures)

🚀 **Production Monitoring**
- [ ] Track failed payments → send dunning emails
- [ ] Monitor subscription churn rate
- [ ] Alert on webhook processing errors
- [ ] Daily reconciliation: Stripe subscriptions vs. DB state

---

**Implementation Owner**: Backend Team  
**Timeline**: Phase 1-2 (2 weeks), Phase 3-4 (1 week)  
**Priority**: High - Enables monetization  
**Dependencies**: Database migration for Subscriptions + UsageMetrics tables
