# 🚀 RAZORPAY SETUP - 3 MINUTE FIX

## ❌ **THE ACTUAL PROBLEM:**

Your Razorpay **API credentials are NOT set in Render environment variables**!

That's why the payment gateway shows as unavailable.

---

## ✅ **3-MINUTE FIX:**

### **STEP 1: Get Keys from Razorpay (1 minute)**

1. Go to **https://dashboard.razorpay.com/**
2. Login to your Razorpay account
3. Click **Settings** → **API Keys** (left sidebar)
4. You'll see:
   - **Key ID** (example: `rzp_test_XXXXXXXXX`)
   - **Key Secret** (long random string)
   - **Webhook Secret** (if available)
5. **Copy all three values**

---

### **STEP 2: Add to Render (1 minute)**

1. Go to **https://render.com/**
2. Login
3. Click your **"suresh-ai-origin"** service
4. Click **Environment** tab (left sidebar)
5. Click **"Add Environment Variable"** button
6. Add these **three variables**:

```
Variable Name: RAZORPAY_KEY_ID
Value: rzp_test_XXXXXXXXX  (paste what you copied)

Variable Name: RAZORPAY_KEY_SECRET
Value: XXXXXXXXX  (paste what you copied)

Variable Name: RAZORPAY_WEBHOOK_SECRET
Value: XXXXXXXXX  (paste what you copied)
```

7. Click **Save**
8. **Wait 2-5 minutes** for Render to auto-deploy

---

### **STEP 3: Test Payment (1 minute)**

1. After deploy finishes, visit: https://suresh-ai-origin.onrender.com/buy?product=starter
2. **You should now see the checkout form** (not the error message)
3. Click "Pay Securely with Razorpay"
4. Razorpay modal should open ✅
5. Use test card: `4111111111111111` (Expiry: 12/25, CVV: 123)

---

## 📋 **COMPLETE ENVIRONMENT SETUP:**

Add ALL these variables to Render:

```
# PAYMENT PROCESSING (REQUIRED for payments)
RAZORPAY_KEY_ID=rzp_test_XXXXXXXXX
RAZORPAY_KEY_SECRET=XXXXXXXXX
RAZORPAY_WEBHOOK_SECRET=XXXXXXXXX

# SECURITY (Recommended)
FLASK_SECRET_KEY=your-random-secret-key-here

# EMAIL (Optional - for order confirmations)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-gmail-app-password

# ADMIN (Optional - for admin access)
ADMIN_TOKEN=your-admin-token-here
```

---

## 🎯 **WHAT HAPPENS AFTER YOU ADD KEYS:**

### **Before (Now):**
```
❌ Visit /buy page
❌ See: "Payment gateway not configured"
❌ Click button → Error
```

### **After (In 5 minutes):**
```
✅ Visit /buy page
✅ See: Razorpay checkout form with price & features
✅ Click "Pay Securely"
✅ Razorpay modal opens
✅ Complete payment with test card
✅ Redirected to success page with download
```

---

## 🧪 **TEST CARD DETAILS:**

When Razorpay modal opens, use this **test card**:

```
Card Number: 4111111111111111
Expiry: 12/25 (or any future date like 12/27)
CVV: 123 (any 3 digits)
```

This is a **free test card** that doesn't charge money.

---

## 📝 **IMPORTANT NOTES:**

### **Test vs Live:**
- **rzp_test_** = Test mode (no real charges, use for testing)
- **rzp_live_** = Live mode (real charges, use for production)

### **Get Test Keys:**
1. Go to https://dashboard.razorpay.com/
2. Make sure **TEST MODE** is toggled ON (top-right)
3. Copy `rzp_test_` keys

### **Switch to Live:**
1. When ready for real payments:
2. Toggle to **LIVE MODE**
3. Copy `rzp_live_` keys
4. Update Render environment variables
5. Restart service

---

## 🚨 **WHAT IF IT STILL DOESN'T WORK:**

### **Check These:**
1. ✅ RAZORPAY_KEY_ID starts with `rzp_test_` or `rzp_live_`
2. ✅ RAZORPAY_KEY_SECRET is not empty
3. ✅ Render has finished deploying (check "Events" tab)
4. ✅ You're visiting the correct URL after adding keys
5. ✅ Try hard refresh: `Ctrl + Shift + R`

### **If Still Failing:**
1. Go to Render dashboard
2. Click service → **Manual Deploy**
3. Click **Deploy** button
4. Wait 3 minutes
5. Try payment page again

---

## 📊 **DEPLOYMENT STATUS:**

✅ Added configuration check in buy.html  
✅ Shows setup instructions if keys are missing  
✅ Redirects to Razorpay dashboard  
✅ Deployed to Render (commit: fc856d7)  
✅ Auto-deploying now

---

## 🎯 **QUICK ACTION:**

1. **Right now:** Copy your Razorpay keys from dashboard.razorpay.com
2. **Next:** Add to Render environment (render.com)
3. **In 5 minutes:** Visit /buy page again
4. **You should see:** Checkout form (no error) ✅

---

**That's it! Payments will work in 5 minutes!** 🚀
