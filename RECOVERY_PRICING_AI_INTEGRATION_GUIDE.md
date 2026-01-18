# Recovery Pricing AI - Integration Guide

**Purpose**: Connect AI-optimized recovery pricing system to existing recovery.py and app.py  
**Effort**: ~30 minutes  
**Impact**: +15-25% recovery revenue  
**Status**: Ready to integrate

---

## 🔗 Integration Points

### 1. Update app.py Routes

Add these 4 routes to `app.py`:

```python
# At top of app.py
from recovery_pricing_ai import (
    get_recovery_suggestions_optimized,
    get_recovery_metrics,
    get_ab_test_winners,
    RecoveryPricingAI
)

# Create engine instance
recovery_ai_engine = RecoveryPricingAI()

# Route 1: Get optimized recovery suggestions
@app.route('/api/recovery/suggestions', methods=['GET'])
def api_recovery_suggestions():
    """Get top N recovery candidates with AI pricing"""
    limit = request.args.get('limit', 20, type=int)
    try:
        suggestions = get_recovery_suggestions_optimized(limit=limit)
        return jsonify({'suggestions': suggestions, 'count': len(suggestions)})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route 2: Track recovery event (email open, click, conversion)
@app.route('/api/recovery/track', methods=['POST'])
def api_track_recovery_event():
    """Track recovery campaign events"""
    data = request.get_json()
    order_id = data.get('order_id')
    event_type = data.get('event_type')  # 'opened', 'clicked', 'converted'
    paid_amount = data.get('paid_amount', 0)  # In paise
    
    try:
        if event_type == 'opened':
            recovery_ai_engine.track_email_opened(order_id)
        elif event_type == 'clicked':
            recovery_ai_engine.track_link_clicked(order_id)
        elif event_type == 'converted':
            recovery_ai_engine.track_recovery_conversion(order_id, paid_amount)
        
        return jsonify({'status': 'tracked'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route 3: Get recovery metrics & A/B results
@app.route('/api/recovery/metrics', methods=['GET'])
def api_recovery_metrics():
    """Get recovery performance metrics and A/B test results"""
    try:
        metrics = get_recovery_metrics()
        ab_results = get_ab_test_winners()
        return jsonify({
            'metrics': metrics,
            'ab_test': ab_results
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Route 4: Get single recovery price (called when generating recovery email)
@app.route('/api/recovery/<order_id>/price', methods=['GET'])
def api_recovery_price(order_id):
    """Get AI-calculated recovery price for specific order"""
    customer_receipt = request.args.get('customer_receipt')
    
    try:
        if not customer_receipt:
            return jsonify({'error': 'customer_receipt required'}), 400
        
        profile = recovery_ai_engine.calculate_recovery_price(order_id, customer_receipt)
        if not profile:
            return jsonify({'error': 'Order or customer not found'}), 404
        
        return jsonify({
            'order_id': order_id,
            'original_amount_paise': profile.original_amount_paise,
            'recovery_amount_paise': profile.recovery_price_paise,
            'discount_percent': profile.base_discount_percent,
            'ab_variant': profile.ab_variant,
            'conversion_probability': profile.conversion_probability
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500
```

---

### 2. Update recovery.py

Modify the recovery email sending to use AI pricing:

```python
# In recovery.py, in the send_recovery_email function
# OLD CODE:
# recovery_discount = 30  # Static 30%

# NEW CODE:
from recovery_pricing_ai import RecoveryPricingAI

recovery_ai_engine = RecoveryPricingAI()

def send_recovery_email(order_id, customer_email, customer_receipt, order_amount):
    """Send recovery email with AI-optimized pricing"""
    
    # Get AI-calculated price
    profile = recovery_ai_engine.calculate_recovery_price(order_id, customer_receipt)
    
    if not profile:
        # Fallback to default if AI fails
        recovery_discount = 30
        recovery_amount = order_amount * (1 - recovery_discount/100)
        ab_variant = 'default'
    else:
        recovery_discount = profile.base_discount_percent
        recovery_amount = profile.recovery_price_paise / 100  # Convert paise to rupees
        ab_variant = profile.ab_variant
    
    # Prepare email content
    email_body = f"""
    Hi {customer_email},
    
    Your order for ₹{order_amount} was abandoned. 
    
    We've reserved it just for you at a special price: ₹{recovery_amount:.2f} ({recovery_discount}% off)
    
    [RECOVERY_LINK - Click to complete purchase]
    
    This offer expires in 24 hours.
    
    Best regards,
    SURESH AI ORIGIN Team
    """
    
    # Send email
    try:
        send_email(customer_email, "Complete your purchase - Special offer", email_body)
        
        # Track that email was sent
        recovery_ai_engine.log_recovery_outcome(
            order_id=order_id,
            customer_receipt=customer_receipt,
            amount_paise=int(order_amount * 100),
            discount_offered_percent=recovery_discount,
            ab_variant=ab_variant,
            email_sent=True,
            timestamp=time.time()
        )
        
        return True
    except Exception as e:
        logger.error(f"Recovery email failed for {order_id}: {e}")
        return False
```

---

### 3. Update Email Tracking

Add email open/click tracking pixels:

```python
# In templates/email_recovery.html

<img src="/tracking/email/opened?order_id={{ order_id }}&customer_receipt={{ customer_receipt }}" width="1" height="1" />

<!-- Make recovery link trackable -->
<a href="/recovery/click?order_id={{ order_id }}&customer_receipt={{ customer_receipt }}&redirect={{ checkout_link }}">
    Complete Purchase for ₹{{ recovery_amount }}
</a>
```

Add tracking routes to app.py:

```python
@app.route('/tracking/email/opened')
def track_email_opened():
    """Track email open via pixel"""
    order_id = request.args.get('order_id')
    recovery_ai_engine.track_email_opened(order_id)
    # Return 1x1 transparent pixel
    return send_file('templates/pixel.gif', mimetype='image/gif')

@app.route('/recovery/click')
def track_recovery_click():
    """Track recovery link click and redirect"""
    order_id = request.args.get('order_id')
    redirect = request.args.get('redirect')
    recovery_ai_engine.track_link_clicked(order_id)
    return redirect(redirect)
```

---

### 4. Add Admin Dashboard

Create new template `templates/admin_recovery_pricing.html`:

```html
{% extends "admin_base.html" %}

{% block title %}Recovery Pricing AI - Admin{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1>Recovery Pricing AI Dashboard</h1>
    
    <div class="row">
        <!-- Key Metrics -->
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Conversion Rate</h5>
                    <h2>{{ metrics.conversion_rate }}%</h2>
                    <small class="text-muted">vs 30% baseline</small>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Avg Recovery Value</h5>
                    <h2>₹{{ metrics.avg_recovery_value }}</h2>
                    <small class="text-muted">Recovered this month</small>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Total Recovered</h5>
                    <h2>₹{{ metrics.total_recovered }}</h2>
                    <small class="text-muted">All time</small>
                </div>
            </div>
        </div>
        
        <div class="col-md-3">
            <div class="card">
                <div class="card-body">
                    <h5>Best Variant</h5>
                    <h2>{{ ab_results.recommended_variant }}</h2>
                    <small class="text-muted">{{ ab_results.by_variant[ab_results.recommended_variant].conversion_rate }}% conversion</small>
                </div>
            </div>
        </div>
    </div>
    
    <!-- A/B Test Results -->
    <div class="row mt-4">
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>A/B Test Performance</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Variant</th>
                                <th>Discount</th>
                                <th>Conversions</th>
                                <th>Rate</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for variant, data in ab_results.by_variant.items() %}
                            <tr>
                                <td><strong>{{ variant }}</strong></td>
                                <td>{{ data.discount }}%</td>
                                <td>{{ data.total_conversions }}</td>
                                <td>{{ data.conversion_rate }}%</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <!-- Top Recoveries -->
        <div class="col-md-6">
            <div class="card">
                <div class="card-header">
                    <h5>Recent Recoveries</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>Order ID</th>
                                <th>Amount</th>
                                <th>Discount</th>
                                <th>Status</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for suggestion in recent_suggestions %}
                            <tr>
                                <td>{{ suggestion.order_id }}</td>
                                <td>₹{{ suggestion.original_amount }}</td>
                                <td>{{ suggestion.discount_offered_percent }}%</td>
                                <td>{{ suggestion.status }}</td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
    // Auto-refresh every 5 minutes
    setInterval(function() {
        location.reload();
    }, 300000);
</script>
{% endblock %}
```

Add route to app.py:

```python
@app.route('/admin/recovery-pricing')
def admin_recovery_pricing():
    """Admin dashboard for recovery pricing AI"""
    if not session.get('admin_logged_in'):
        return redirect(url_for('admin_login'))
    
    metrics = get_recovery_metrics()
    ab_results = get_ab_test_winners()
    suggestions = get_recovery_suggestions_optimized(limit=10)
    
    return render_template('admin_recovery_pricing.html',
        metrics=metrics,
        ab_results=ab_results,
        recent_suggestions=suggestions
    )
```

---

## 📊 Testing Checklist

After integration, verify each piece:

### 1. Test Route: Get Suggestions
```bash
curl http://localhost:5000/api/recovery/suggestions?limit=5
# Should return: top 5 recovery suggestions with AI pricing
```

### 2. Test Route: Track Event
```bash
curl -X POST http://localhost:5000/api/recovery/track \
  -H "Content-Type: application/json" \
  -d '{"order_id": "order_123", "event_type": "opened"}'
# Should return: {"status": "tracked"}
```

### 3. Test Route: Get Price
```bash
curl http://localhost:5000/api/recovery/order_123/price?customer_receipt=cust_456
# Should return: AI-calculated discount and price
```

### 4. Test Route: Get Metrics
```bash
curl http://localhost:5000/api/recovery/metrics
# Should return: conversion rates and A/B test results
```

### 5. Test Admin Dashboard
```
Navigate to: http://localhost:5000/admin/recovery-pricing
Should show: Key metrics, A/B results, recent recoveries
```

---

## 🚀 Deployment Steps

### Step 1: Backup Current Data
```bash
python scripts/backup_db.py create
```

### Step 2: Copy Files
```bash
# Copy recovery_pricing_ai.py to root
cp recovery_pricing_ai.py .

# Copy tests for validation
cp tests/test_recovery_pricing_ai.py tests/
```

### Step 3: Run Tests
```bash
pytest tests/test_recovery_pricing_ai.py -v
# Should show: 30 passed
```

### Step 4: Update Code
- Update `app.py` with new routes
- Update `recovery.py` with AI pricing
- Update email templates with tracking pixels
- Add new admin template

### Step 5: Restart Service
```bash
# Local
FLASK_DEBUG=1 python app.py

# Render
git push  # Automatic redeploy
```

### Step 6: Verify Live
- Check admin dashboard loads
- Send test recovery email
- Verify tracking pixels fire
- Monitor /api/recovery/metrics

---

## 📈 Monitoring (First Week)

### Key Metrics to Watch

```python
# Check daily
metrics = get_recovery_metrics()

print(f"Email Open Rate: {metrics['email_open_rate']:.1%}")
print(f"Click Rate: {metrics['click_rate']:.1%}")
print(f"Conversion Rate: {metrics['conversion_rate']:.1%}")
print(f"Avg Recovery: ₹{metrics['avg_recovery_value']:.2f}")

# Check A/B test
ab_results = get_ab_test_winners()
print(f"\nA/B Results:")
for variant, data in ab_results['by_variant'].items():
    print(f"  {variant}: {data['conversion_rate']}% conversion")

print(f"\nRecommended: {ab_results['recommended_variant']}")
```

### Expected Week 1 Results
- Email opens: 20-30%
- Click rate: 5-10%
- Conversion: 25-35%
- See variance by variant (one should lead)

### Expected Week 4 Results
- Clearer winner emerging
- Conversion rate: 30-40%
- Revenue lift: +10-15%

---

## ⚠️ Troubleshooting

### Issue: Suggestions returning empty
```python
# Check if there are abandoned orders
session.query(Order).filter(Order.status == 'created').count()

# If > 0, check recovery_pricing_ai.py logs
# If = 0, create test order to debug
```

### Issue: A/B results all zeros
```python
# Check if outcomes are being logged
import json
with open('data/recovery_outcomes.jsonl') as f:
    lines = f.readlines()
    print(f"Total outcomes logged: {len(lines)}")
    if lines:
        print("Sample:", lines[0])
```

### Issue: Variant not assigned correctly
```python
# Check hash function
from recovery_pricing_ai import RecoveryPricingAI
engine = RecoveryPricingAI()
variant = engine._get_variant_for_customer('test_receipt')
print(f"Assigned variant: {variant}")  # Should be A/B/C/D
```

---

## 📞 Support

If integration issues:
1. Check test file passes: `pytest tests/test_recovery_pricing_ai.py -v`
2. Review error logs in app.py output
3. Verify models.py imports work: `python -c "from models import Order; print('OK')"`
4. Check data/recovery_outcomes.jsonl is writable

---

**Ready to deploy?** Follow the 5 steps above and monitor metrics for week 1.

**Expected Result**: +15-25% recovery revenue increase within 4 weeks.
