# 🚀 Referral Program System

**Exponential Growth Through God's Community** - Complete referral and affiliate program for viral customer acquisition.

## 🎯 Overview

The referral program enables **exponential growth** by turning customers into ambassadors. Every satisfied customer can refer others and earn commission - creating a self-sustaining viral growth engine.

### Key Features
- ✅ **Unique Referral Codes** - Every customer gets a personal code
- ✅ **Generous Commission** - 20-30% commission on referrals
- ✅ **Tier Bonuses** - Extra commission for Premium referrals
- ✅ **Leaderboard** - Gamification drives competition
- ✅ **Automated Tracking** - From click to conversion to payout
- ✅ **₹1000 Minimum Payout** - Ensures meaningful withdrawals
- ✅ **Beautiful Dashboard** - Track all referrer activity

---

## 💰 Commission Structure

### Base Commission: **20%**
Every referral earns 20% of the order value.

### Tier Bonuses
- **Starter Pack**: 0% bonus → **20% total**
- **Pro Pack**: +5% bonus → **25% total**
- **Premium Pack**: +10% bonus → **30% total**

### Payout Terms
- **Minimum**: ₹1000 (100,000 paise)
- **Cookie Duration**: 30 days
- **Status**: PENDING → CONVERTED → PAID

---

## 🛠️ Core Functions

### `create_referral_program(receipt, name=None)`
Creates a referral program for a customer.

**Args:**
- `receipt` (str): Customer receipt ID
- `name` (str, optional): Referrer's name

**Returns:**
```python
{
    'referral_code': 'TEST_CUS1234',
    'referrer_receipt': 'TEST_CUSTOMER_123',
    'referrer_name': 'John Doe',
    'commission_percent': 20,
    'status': 'CREATED'
}
```

**Example:**
```python
program = create_referral_program('CUST_123', 'John Doe')
print(f"Share your code: {program['referral_code']}")
```

---

### `record_referral(referral_code, referred_receipt, order_id, amount_paise, product=None)`
Records a new referral when someone uses a referral code.

**Args:**
- `referral_code` (str): Referral code used
- `referred_receipt` (str): New customer's receipt
- `order_id` (str): Order ID from purchase
- `amount_paise` (int): Order amount in paise
- `product` (str, optional): Product name (for tier bonus)

**Returns:**
```python
{
    'referral_id': 'REF_1704975600_abc123',
    'commission_amount_paise': 9980,
    'commission_amount_rupees': 99.80,
    'commission_percent': 20,
    'status': 'PENDING'
}
```

**Example:**
```python
result = record_referral('JOHNDOE1234', 'CUST_456', 'ORDER_789', 49900, 'pro_pack')
print(f"Commission: ₹{result['commission_amount_rupees']}") # ₹124.75 (25%)
```

---

### `convert_referral(order_id)`
Marks referral as converted when payment completes.

**Args:**
- `order_id` (str): Order ID that was paid

**Returns:**
- `bool`: True if successful, False if not found

**Example:**
```python
# Call this in webhook when payment.captured
convert_referral(order_id)
```

---

### `get_referral_stats(receipt)`
Get referral statistics for a customer.

**Args:**
- `receipt` (str): Referrer's receipt ID

**Returns:**
```python
{
    'referral_code': 'JOHNDOE1234',
    'referrer_name': 'John Doe',
    'total_referrals': 10,
    'successful_referrals': 7,
    'conversion_rate': 70.0,
    'pending_commission_paise': 69860,
    'pending_commission_rupees': 698.60,
    'paid_commission_paise': 50000,
    'paid_commission_rupees': 500.00,
    'total_earned_paise': 119860,
    'total_earned_rupees': 1198.60,
    'can_withdraw': False  # Below ₹1000 minimum
}
```

---

### `get_pending_payouts()`
Get referrers ready for commission payout.

**Returns:**
```python
[
    {
        'referrer_receipt': 'CUST_123',
        'referrer_name': 'John Doe',
        'referral_code': 'JOHNDOE1234',
        'pending_paise': 119860,
        'pending_rupees': 1198.60,
        'referral_count': 7
    }
]
```

---

### `process_payout(receipt)`
Process commission payout for referrer.

**Args:**
- `receipt` (str): Referrer's receipt ID

**Returns:**
```python
{
    'success': True,
    'payout_amount_paise': 119860,
    'payout_amount_rupees': 1198.60,
    'referral_count': 7
}
```

**Example:**
```python
result = process_payout('CUST_123')
if result.get('success'):
    print(f"Paid ₹{result['payout_amount_rupees']} for {result['referral_count']} referrals")
```

---

### `get_referral_leaderboard(limit=20)`
Get referral leaderboard.

**Returns:**
```python
[
    {
        'rank': 1,
        'referrer_name': 'Top Referrer',
        'referral_code': 'TOPREFER1234',
        'successful_referrals': 50,
        'total_earned_rupees': 9980.00,
        'conversion_rate': 83.3
    }
]
```

---

### `get_referral_analytics()`
Get overall referral program analytics.

**Returns:**
```python
{
    'total_referrers': 25,
    'total_referrals': 150,
    'successful_referrals': 105,
    'conversion_rate_percent': 70.0,
    'total_commission_paise': 209790,
    'total_commission_rupees': 2097.90,
    'paid_commission_paise': 100000,
    'paid_commission_rupees': 1000.00,
    'pending_commission_paise': 109790,
    'pending_commission_rupees': 1097.90,
    'average_commission_per_referral': 19.98
}
```

---

## 📊 Database Schema

### ReferralProgram Table
```sql
CREATE TABLE referral_programs (
    referral_code TEXT PRIMARY KEY,
    referrer_receipt TEXT UNIQUE INDEXED,
    referrer_name TEXT NULL,
    commission_percent INTEGER,
    total_referrals INTEGER DEFAULT 0,
    successful_referrals INTEGER DEFAULT 0,
    total_commission_paise INTEGER DEFAULT 0,
    total_paid_paise INTEGER DEFAULT 0,
    created_at REAL
);
```

### Referral Table
```sql
CREATE TABLE referrals (
    id TEXT PRIMARY KEY,
    referral_code TEXT INDEXED,
    referrer_receipt TEXT INDEXED,
    referred_receipt TEXT INDEXED,
    order_id TEXT INDEXED,
    order_amount_paise INTEGER,
    commission_percent INTEGER,
    commission_amount_paise INTEGER,
    status TEXT INDEXED,  -- PENDING, CONVERTED, PAID, CANCELLED
    converted_at REAL NULL,
    paid_at REAL NULL,
    created_at REAL
);
```

---

## 🌐 API Endpoints

### `GET /admin/referrals`
Admin dashboard for referral program.

**Response:** HTML dashboard with:
- Key metrics (referrers, referrals, conversion rate, commission)
- Pending payouts ready for processing
- Leaderboard (top 20 referrers)
- All referrers table

---

### `POST /api/referrals/create`
Create referral program for customer.

**Request:**
```json
{
    "receipt": "CUST_123",
    "name": "John Doe"
}
```

**Response:**
```json
{
    "referral_code": "CUST_1231234",
    "referrer_receipt": "CUST_123",
    "referrer_name": "John Doe",
    "commission_percent": 20,
    "status": "CREATED"
}
```

---

### `POST /api/referrals/record`
Record a referral (public endpoint).

**Request:**
```json
{
    "referral_code": "JOHNDOE1234",
    "referred_receipt": "CUST_456",
    "order_id": "ORDER_789",
    "amount_paise": 49900,
    "product": "pro_pack"
}
```

**Response:**
```json
{
    "referral_id": "REF_1704975600_abc123",
    "commission_amount_paise": 12475,
    "commission_amount_rupees": 124.75,
    "commission_percent": 25,
    "status": "PENDING"
}
```

---

### `GET /api/referrals/stats/<receipt>`
Get referral stats for a customer.

**Response:**
```json
{
    "referral_code": "JOHNDOE1234",
    "total_referrals": 10,
    "successful_referrals": 7,
    "conversion_rate": 70.0,
    "pending_commission_rupees": 698.60,
    "can_withdraw": false
}
```

---

### `POST /api/referrals/payout/<receipt>`
Process commission payout.

**Response:**
```json
{
    "success": true,
    "payout_amount_rupees": 1198.60,
    "referral_count": 7
}
```

---

## 🧪 Test Coverage

**19 comprehensive tests** covering all functionality:

### Creation & Setup (3 tests)
- ✅ Generate referral code
- ✅ Create referral program
- ✅ Duplicate program returns existing

### Recording Referrals (3 tests)
- ✅ Record referral successfully
- ✅ Invalid code validation
- ✅ Tier bonus calculation (STARTER/PRO/PREMIUM)

### Conversion (2 tests)
- ✅ Convert referral on payment
- ✅ Invalid order handling

### Statistics (2 tests)
- ✅ Get referral stats
- ✅ Nonexistent program handling

### Referrer Lists (2 tests)
- ✅ Get all referrers (sorted by earnings)
- ✅ Get top referrers

### Payouts (4 tests)
- ✅ Get pending payouts (above minimum)
- ✅ Process payout successfully
- ✅ Below minimum validation
- ✅ No pending commission handling

### Analytics (2 tests)
- ✅ Leaderboard generation
- ✅ Overall program analytics

### Configuration (1 test)
- ✅ Commission structure validation

**Run tests:**
```bash
pytest tests/test_referrals.py -v
```

---

## 💡 Growth Impact Scenarios

### Scenario 1: 100 Customers, 10% Refer
- **Active referrers**: 10 customers
- **Average referrals each**: 5 customers
- **Total new customers**: 50 (50% growth!)
- **Average order**: ₹499 (Pro pack)
- **Commission per referrer**: ₹622.50
- **Total commission paid**: ₹6,225
- **New revenue**: ₹24,950
- **Net revenue**: ₹18,725 (75% after commission)

### Scenario 2: Viral Loop (3 Generations)
- **Gen 1**: 10 referrers → 50 new customers
- **Gen 2**: 5 referrers (10% of 50) → 25 new customers
- **Gen 3**: 2 referrers (10% of 25) → 10 new customers
- **Total new customers**: 85 (85% growth!)
- **Total commission**: ₹10,580
- **Total revenue**: ₹42,415
- **Net revenue**: ₹31,835

### Scenario 3: Subscription + Referral Combo
- **Monthly subscribers**: 100 at ₹499/month = ₹49,900 MRR
- **Referral growth**: +50 subscribers/month
- **Month 1**: 100 subscribers + 50 = 150 (₹74,850 MRR)
- **Month 2**: 150 + 75 = 225 (₹112,275 MRR)
- **Month 3**: 225 + 112 = 337 (₹168,163 MRR)
- **3-month growth**: **237% increase in MRR!**

---

## 📈 Admin Dashboard

Beautiful gradient purple dashboard at `/admin/referrals`:

### Metrics Cards (4)
1. **Total Referrers** - Active ambassadors count
2. **Total Referrals** - All referrals (successful count)
3. **Conversion Rate** - Success percentage with color coding
4. **Total Commission** - Earned (pending shown)

### Pending Payouts Section
- Gradient pink/red cards for each payout ready
- Shows referrer name, code, amount, referral count
- "Pay Out" button processes payout instantly

### Leaderboard
- Top 20 referrers by earnings
- Gold/Silver/Bronze medals for top 3
- Referral code, count, conversion rate, earnings
- Color-coded conversion rates (green/yellow/red)

### All Referrers Table
- Comprehensive view of every referrer
- Stats: total, successful, conversion, pending, paid
- "Can Withdraw" or "Accumulating" status badges

---

## 🔥 Integration Flow

### 1. Customer Makes Purchase
```python
# In /success route or webhook
from referrals import create_referral_program

# Auto-create referral program
program = create_referral_program(receipt, customer_name)
referral_code = program['referral_code']

# Show in UI or email
print(f"Your referral code: {referral_code}")
print(f"Share and earn 20-30% commission!")
```

### 2. Referred Customer Clicks Link
```
https://yourdomain.com/buy?ref=JOHNDOE1234
```

Store `ref` in session/cookie for 30 days.

### 3. Referred Customer Purchases
```python
# In /success route after payment
from referrals import record_referral

ref_code = request.cookies.get('referral_code')
if ref_code:
    result = record_referral(
        referral_code=ref_code,
        referred_receipt=new_customer_receipt,
        order_id=order_id,
        amount_paise=order_amount,
        product=product
    )
```

### 4. Payment Webhook Converts
```python
# In /webhook route
from referrals import convert_referral

if event == 'payment.captured':
    order_id = payload['order_id']
    convert_referral(order_id)  # Marks commission as earned
```

### 5. Admin Processes Payout
Use dashboard or API:
```python
from referrals import process_payout

# When ready to pay
result = process_payout(referrer_receipt)
# Then transfer ₹amount via bank/Razorpay
```

---

## ✅ Deployment Checklist

- [x] Core module created (`referrals.py`)
- [x] Database tables added (ReferralProgram, Referral)
- [x] Routes added to Flask app (6 endpoints)
- [x] Admin dashboard created (beautiful UI)
- [x] Test suite complete (19 tests, all passing)
- [x] Commission structure configured
- [x] Tier bonuses implemented
- [x] Payout validation (₹1000 minimum)
- [x] Leaderboard gamification
- [x] Analytics tracking

---

## 🎯 Next Steps

1. **Frontend Integration**
   - Add referral code to customer dashboard
   - Create shareable referral links
   - Show commission earned in real-time

2. **Share Features**
   - One-click share to WhatsApp, Email, Twitter
   - Pre-filled messages with code
   - QR codes for offline sharing

3. **Enhanced Tracking**
   - Track referral link clicks
   - A/B test different commission rates
   - Cohort analysis of referred customers

4. **Automated Payouts**
   - Integrate Razorpay Payout API
   - Auto-pay when minimum reached
   - Bank account verification

5. **Incentives & Bonuses**
   - Monthly top referrer bonuses
   - Milestone rewards (10, 25, 50 referrals)
   - Limited-time double commission campaigns

6. **Communication**
   - Weekly stats email to referrers
   - New referral notifications
   - Payout confirmation emails

---

## 🙏 God's Principle: Community Growth

*"Iron sharpens iron, and one person sharpens another." - Proverbs 27:17*

The referral program embodies God's principle of **community multiplication**:
- Blessed customers **bless others** by sharing
- Everyone wins - referrer earns, referred saves/benefits
- Creates **exponential growth** through genuine community
- Rewards faithful ambassadors for their service
- Builds a self-sustaining ecosystem of mutual blessing

**Through faith, one customer becomes 10, 10 becomes 100, 100 becomes 1000! 🙏✨**

---

## 📊 System Status

✅ **PRODUCTION READY**

- 19/19 tests passing (100%)
- All core functions operational
- Beautiful admin dashboard
- Complete API coverage
- Comprehensive documentation
- Ready for customer referrals!

Access dashboard: `http://localhost:5000/admin/referrals`

**May God bless this program with exponential viral growth! 🚀🙏**
