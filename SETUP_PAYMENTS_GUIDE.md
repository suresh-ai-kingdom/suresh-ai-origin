# 💰 PAYMENT SETUP GUIDE - SURESH AI ORIGIN

## Current Status: ⚠️ DEMO MODE (No Real Payments Yet)

### Why Payments Not Working:
1. **Razorpay keys NOT configured** in environment variables
2. **Crypto wallets** are demo addresses (not real)
3. **Webhooks** not receiving payment confirmations
4. **Bank account** not linked to Razorpay

---

## 🚀 STEP-BY-STEP FIX (Get Money Flowing)

### **STEP 1: Create Razorpay Account** (5 minutes)

1. Go to: https://razorpay.com/
2. Click "Sign Up" → Enter your details
3. Complete KYC:
   - Pan Card
   - Aadhaar
   - Bank Account (where you want money)
   - Business/Individual details
4. Wait for approval (usually 24-48 hours)

### **STEP 2: Get API Keys** (2 minutes)

Once approved:
1. Login to Razorpay Dashboard
2. Go to **Settings** → **API Keys**
3. Click **Generate Test Key** (for testing first)
4. Copy both:
   - `key_id` (starts with `rzp_test_`)
   - `key_secret` (long random string)

### **STEP 3: Configure Environment on Render** (3 minutes)

1. Go to Render Dashboard: https://dashboard.render.com/
2. Select your `suresh-ai-origin` service
3. Click **Environment** tab
4. Add these variables:

```bash
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=your_webhook_secret_here
```

5. Click **Save Changes** → Service will auto-restart

### **STEP 4: Setup Webhook** (5 minutes)

Razorpay needs to notify your app when payment succeeds:

1. In Razorpay Dashboard → **Settings** → **Webhooks**
2. Click **Create Webhook**
3. Enter:
   - **Webhook URL**: `https://suresh-ai-origin.onrender.com/webhook`
   - **Secret**: Create a strong password (save it!)
   - **Events**: Select `payment.captured`, `payment.failed`
4. Click **Create**
5. Copy the **Webhook Secret** and add to Render environment as `RAZORPAY_WEBHOOK_SECRET`

### **STEP 5: Test Payment Flow** (5 minutes)

1. Visit: https://suresh-ai-origin.onrender.com/
2. Click any **"Explore Products"** or **"Pay with Crypto"** button
3. Use Razorpay **Test Card**:
   - Card Number: `4111 1111 1111 1111`
   - CVV: `123`
   - Expiry: Any future date
   - OTP: `123456`
4. Complete payment
5. Check `/admin/orders` to see if order appears as PAID

### **STEP 6: Go LIVE (Start Receiving Real Money)** (5 minutes)

Once test works:
1. In Razorpay Dashboard → **Settings** → **API Keys**
2. Click **Generate Live Key**
3. Replace environment variables on Render:
   ```bash
   RAZORPAY_KEY_ID=rzp_live_xxxxxxxxxxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxxxxxxxxxxxxxxx
   ```
4. Update webhook URL to use LIVE mode
5. **Now you'll receive REAL payments!** 💰

---

## 💎 CRYPTO PAYMENT SETUP

### **STEP 1: Get Your Crypto Wallets**

1. **Bitcoin (BTC)**:
   - Download: Trust Wallet / Coinbase
   - Get your BTC address (starts with `bc1` or `1`)

2. **Ethereum (ETH)**:
   - Same wallet as BTC
   - Get your ETH address (starts with `0x`)

3. **USDT (Tether)**:
   - Use TRC-20 (cheaper fees) or ERC-20
   - Get USDT address

4. **Solana (SOL)**:
   - Download: Phantom Wallet
   - Get SOL address

### **STEP 2: Update Crypto Wallets in Code**

Edit `static/crypto-effects.js` (lines 186-191):

```javascript
const walletAddresses = {
    bitcoin: 'YOUR_REAL_BTC_ADDRESS',
    ethereum: 'YOUR_REAL_ETH_ADDRESS',
    usdt: 'YOUR_REAL_USDT_TRC20_ADDRESS',
    solana: 'YOUR_REAL_SOL_ADDRESS'
};
```

### **STEP 3: Manual Verification Process**

Since crypto is decentralized:
1. Customer pays to your wallet
2. They email you transaction ID
3. You verify on blockchain explorer:
   - Bitcoin: https://blockchain.com/
   - Ethereum: https://etherscan.io/
   - Solana: https://solscan.io/
4. Once confirmed → manually mark order as PAID in admin

---

## 📊 CHECKING REVENUE

### View Real-Time Payments:
- **Orders Dashboard**: https://suresh-ai-origin.onrender.com/admin/orders
- **Webhooks Log**: https://suresh-ai-origin.onrender.com/admin/webhooks
- **Revenue Stats**: https://suresh-ai-origin.onrender.com/admin/executive

### Expected Revenue Flow:
```
Customer Pays ₹499 
  ↓
Razorpay (deducts 2% fee = ₹10)
  ↓
Your Bank Account (₹489)
  ↓
Settlement Time: T+2 days (2 business days)
```

---

## ⚠️ COMMON ISSUES

### "No money in account" → Check:
1. ✅ Razorpay KYC approved?
2. ✅ Test mode vs Live mode?
3. ✅ Webhook secret correct?
4. ✅ Bank account linked in Razorpay?
5. ✅ Settlement cycle (2 days wait)?

### "Automations not working" → Check:
1. Go to `/admin/automations`
2. Click **"Trigger Now"** on each workflow
3. Check **"Recent Executions"** table
4. If errors → check `/admin` for logs

---

## 🔧 QUICK DEBUG COMMANDS

```bash
# Check if Razorpay configured
curl https://suresh-ai-origin.onrender.com/admin

# Test create order (should return order_id)
curl -X POST https://suresh-ai-origin.onrender.com/api/orders/create \
  -H "Content-Type: application/json" \
  -d '{"amount": 99, "product": "starter"}'

# Check webhooks received
curl https://suresh-ai-origin.onrender.com/admin/webhooks
```

---

## 💡 NEXT STEPS AFTER SETUP

1. **Test with ₹1 payment** first
2. **Verify bank settlement** (2 days)
3. **Enable live mode**
4. **Share payment link** with customers
5. **Monitor dashboard** daily for orders

---

## 🆘 NEED HELP?

If still not working after this:
1. Check Render logs for errors
2. Verify all environment variables set
3. Test webhook with Razorpay's webhook tester
4. Email support@razorpay.com for payment issues

**Expected Timeline**:
- Razorpay KYC: 24-48 hours
- First test payment: 5 minutes
- First real settlement: 2-3 business days

**Bottom Line**: You need to complete Razorpay KYC + add API keys to Render environment variables. That's it! 🚀
