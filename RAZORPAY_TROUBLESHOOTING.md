# 🔧 RAZORPAY PAYMENT TROUBLESHOOTING

## ❌ ERROR: "Failed to initiate payment. Please try again"

This means the `/create_order` endpoint is failing. Here's how to fix it:

---

## 🔍 ROOT CAUSE ANALYSIS

### Error Flow:
```
Click "Pay Securely" button
    ↓
JavaScript calls POST /create_order
    ↓
/create_order returns error (not JSON order)
    ↓
JavaScript catch block fires
    ↓
"Failed to initiate payment. Please try again"
```

### Most Common Causes:

1. **❌ RAZORPAY_KEY_ID not set in Render environment**
2. **❌ RAZORPAY_KEY_SECRET not set in Render environment**
3. **❌ Razorpay credentials are invalid/expired**
4. **❌ Network/firewall issue blocking Razorpay API**
5. **❌ Database error saving order**

---

## ✅ STEP-BY-STEP FIX

### STEP 1: Check Render Environment Variables

1. Go to https://render.com/
2. Click on your "suresh-ai-origin" service
3. Click "Environment" tab
4. Look for these variables:

```
RAZORPAY_KEY_ID = rzp_test_xxxxx (or rzp_live_xxxxx)
RAZORPAY_KEY_SECRET = xxxxxxxxx
RAZORPAY_WEBHOOK_SECRET = xxxxxxxxx
```

**If any are MISSING:**

a) Log in to https://dashboard.razorpay.com/
b) Go to Settings → API Keys
c) Copy your **Key ID** and **Key Secret**
d) Go back to Render
e) Click "Environment" 
f) Add/update the variables:

```
RAZORPAY_KEY_ID=rzp_test_xxxxx
RAZORPAY_KEY_SECRET=your-secret-key
RAZORPAY_WEBHOOK_SECRET=your-webhook-secret
```

g) Click "Save"
h) Render will auto-redeploy with new variables (2-5 minutes)

---

### STEP 2: Verify Variables Are Correct

**Get your actual Razorpay keys:**

1. Go to https://dashboard.razorpay.com/
2. Click "Settings" → "API Keys"
3. You should see:
   - **Key ID**: Starts with `rzp_test_` or `rzp_live_`
   - **Key Secret**: Long string of characters

**For TESTING (sandbox mode):**
```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
```

**For PRODUCTION (live):**
```
RAZORPAY_KEY_ID=rzp_live_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
```

---

### STEP 3: Check Render Logs for Detailed Errors

1. Go to Render dashboard
2. Click your service
3. Click "Logs" tab
4. Look for error messages like:

```
ERROR: Razorpay API error
ERROR: Razorpay payment attempt but RAZORPAY_KEY_ID not configured
ERROR: Failed to create payment order
```

**What different errors mean:**

| Error | Cause | Fix |
|-------|-------|-----|
| `RAZORPAY_KEY_ID not configured` | Environment var not set | Add to Render env vars |
| `unauthorized` | Invalid key/secret | Check Razorpay dashboard |
| `connection error` | Network issue | Check Razorpay API status |
| `order.create failed` | Razorpay API error | Check Razorpay docs |

---

### STEP 4: Test the Payment Flow

#### Test 1: Check if /create_order endpoint works

Open browser console (F12) and run:

```javascript
fetch('/create_order', {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({
        amount: 99,
        product: 'starter'
    })
})
.then(r => r.json())
.then(data => console.log(data))
.catch(e => console.error(e))
```

**Expected response:**
```json
{
  "id": "order_xxxxx",
  "entity": "order",
  "amount": 9900,
  "currency": "INR",
  "status": "created",
  "receipt": "receipt#xxxxxxxxx"
}
```

**If you get error instead:**
```json
{
  "error": "payment_gateway_not_configured",
  "message": "Payment processing is not available",
  "details": "RAZORPAY_KEY_ID and RAZORPAY_KEY_SECRET must be configured"
}
```

→ **Your environment variables are NOT set!**

---

#### Test 2: Check if Razorpay SDK loads

1. Visit https://suresh-ai-origin.onrender.com/buy?product=starter
2. Open browser console (F12)
3. Type: `typeof Razorpay`
4. **Expected:** `"function"`
5. **If error:** Razorpay script didn't load (network issue)

---

#### Test 3: Monitor Network Requests

1. Visit https://suresh-ai-origin.onrender.com/buy?product=starter
2. Open DevTools (F12) → Network tab
3. Click "Pay Securely with Razorpay" button
4. Look for POST request to `/create_order`
5. Check response:
   - **Success:** Status 200, contains `id` field
   - **Failure:** Status 503 or 502, contains `error` field

---

## 🚀 QUICK DEPLOYMENT FIX

### If you just added/updated environment variables:

1. Go to Render.com
2. Click your service → "Manual Deploy"
3. Click "Deploy" button
4. Wait 2-5 minutes for rebuild
5. Test payment page again

**Or** wait for auto-deploy (if you pushed changes to GitHub)

---

## 📊 DEBUGGING CHECKLIST

- [ ] RAZORPAY_KEY_ID is set in Render
- [ ] RAZORPAY_KEY_SECRET is set in Render
- [ ] Both values are correct (from dashboard.razorpay.com)
- [ ] Render auto-deployed after adding variables
- [ ] `/create_order` returns JSON with order ID
- [ ] Browser console shows no errors
- [ ] Razorpay SDK loaded (`typeof Razorpay === 'function'`)
- [ ] Network request shows 200 status

---

## 🎯 WHAT TO EXPECT AFTER FIX

### Before (Broken):
```
Click "Pay Securely"
  ↓
"Failed to initiate payment. Please try again"
```

### After (Working):
```
Click "Pay Securely"
  ↓
Razorpay modal opens
  ↓
Enter test card details:
  - Card: 4111111111111111
  - Expiry: Any future date
  - CVV: Any 3 digits
  ↓
"Payment completed successfully"
  ↓
Redirected to /success page
  ↓
Download link available
```

---

## 🧪 TEST WITH RAZORPAY TEST KEYS

To test payments without charging real money:

1. Go to https://dashboard.razorpay.com/
2. Make sure you're in **TEST MODE** (toggle in top-right)
3. Copy Key ID and Key Secret from Settings → API Keys
4. Add to Render environment:
   ```
   RAZORPAY_KEY_ID=rzp_test_xxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxx
   ```

5. Use **test card** to make payment:
   ```
   Card Number: 4111111111111111
   Expiry: Any future date (e.g., 12/25)
   CVV: Any 3 digits (e.g., 123)
   ```

6. Complete payment → check success page

---

## 💳 SWITCHING TO LIVE MODE

When ready to accept real payments:

1. Go to https://dashboard.razorpay.com/
2. Toggle to **LIVE MODE** (top-right)
3. Copy **LIVE** Key ID and Key Secret
4. Update Render environment:
   ```
   RAZORPAY_KEY_ID=rzp_live_xxxxx
   RAZORPAY_KEY_SECRET=xxxxxxxxx
   ```
5. Save and wait for auto-deploy

---

## 🔒 SECURITY NOTE

**NEVER:**
- Put Razorpay keys in code (use environment variables only)
- Share your Key Secret publicly
- Use live keys in test environment

**ALWAYS:**
- Use test keys for development
- Rotate keys regularly
- Store in Render environment (not .env file)

---

## 📞 SUPPORT

**If still having issues:**

1. Check Render logs for specific error messages
2. Verify keys are from https://dashboard.razorpay.com/
3. Make sure you're using `rzp_test_` for test mode
4. Try manual deploy in Render dashboard
5. Clear browser cache (Ctrl+Shift+Delete)
6. Try different browser
7. Check Razorpay status page: https://status.razorpay.com/

---

## 📝 QUICK ENVIRONMENT SETUP

**Copy and paste into Render Environment:**

```
# Razorpay API Credentials (required for payments)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxx

# Flask Security
FLASK_SECRET_KEY=your-random-secret-key

# Email Notifications
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# Admin Access (optional)
ADMIN_TOKEN=your-admin-token
ADMIN_USERNAME=admin
ADMIN_PASSWORD=secure-password
```

Then click **Save** and **Manual Deploy**

---

**Status:** ✅ Debug logging added  
**Next:** Check Razorpay credentials in Render environment  
**Support:** Check Render logs for specific error messages
