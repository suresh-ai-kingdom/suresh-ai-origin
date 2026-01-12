# ⚡ RAZORPAY PAYMENT FIX - QUICK ACTION ITEMS

## 🔴 YOUR CURRENT ISSUE
```
Click "Pay Securely with Razorpay"
  ↓
"Failed to initiate payment. Please try again"
```

## ✅ FIX IN 3 MINUTES

### STEP 1: Get Your Razorpay Keys (1 minute)

1. Go to https://dashboard.razorpay.com/
2. Click **Settings** → **API Keys** (left sidebar)
3. You'll see:
   - **Key ID** (starts with `rzp_test_` or `rzp_live_`)
   - **Key Secret** (long random string)
4. Make sure you're in **TEST MODE** (toggle in top-right)
5. Copy both values

---

### STEP 2: Add Keys to Render (1 minute)

1. Go to https://render.com/
2. Click your **suresh-ai-origin** service
3. Click **Environment** tab
4. Click **Add Environment Variable**
5. Add these three variables:

```
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxx
```

(Replace `xxxxxxxxx` with your actual values from Razorpay)

6. Click **Save**
7. Render will auto-redeploy (takes 2-5 minutes)

---

### STEP 3: Test Payment (1 minute)

1. Wait 3 minutes for Render to rebuild
2. Visit https://suresh-ai-origin.onrender.com/buy?product=starter
3. Click "Pay Securely with Razorpay"
4. Razorpay modal should now open
5. Use **test card**:
   ```
   Card: 4111111111111111
   Expiry: 12/25 (or any future date)
   CVV: 123 (any 3 digits)
   ```
6. Complete payment
7. You should see success page with download link ✅

---

## 🔧 IF STILL NOT WORKING

**Check Render Logs:**
1. Go to Render dashboard
2. Click service → **Logs** tab
3. Look for errors about Razorpay
4. Copy the error and check [RAZORPAY_TROUBLESHOOTING.md](./RAZORPAY_TROUBLESHOOTING.md)

**Or try these:**
- [ ] Hard refresh page (Ctrl+Shift+R)
- [ ] Clear browser cache
- [ ] Try different browser
- [ ] Check Razorpay status: https://status.razorpay.com/
- [ ] Make sure you're in TEST MODE on Razorpay

---

## 🎯 WHAT YOU'LL HAVE AFTER FIX

✅ Click "Pay Securely" → Razorpay modal opens  
✅ Complete payment with test card  
✅ See success page with download link  
✅ Download your product  
✅ Real payments will work once you switch to LIVE mode  

---

## 📝 ENVIRONMENT VARIABLES NEEDED

Add these to Render → Environment:

```
# PAYMENT (REQUIRED for payments to work)
RAZORPAY_KEY_ID=rzp_test_xxxxxxxxx
RAZORPAY_KEY_SECRET=xxxxxxxxx
RAZORPAY_WEBHOOK_SECRET=xxxxxxxxx

# SECURITY (Recommended)
FLASK_SECRET_KEY=your-random-secret-key

# EMAIL (Optional - for order confirmations)
EMAIL_USER=your-email@gmail.com
EMAIL_PASS=your-app-password

# ADMIN (Optional - for admin access)
ADMIN_TOKEN=your-admin-token
```

Then click **Save** and wait 2-5 minutes for auto-deploy.

---

## 🚀 NEXT STEPS

1. ✅ Add Razorpay keys to Render
2. ✅ Wait for auto-deploy (2-5 minutes)
3. ✅ Test payment flow
4. ✅ Celebrate when it works! 🎉

Done in **3 minutes!**

---

**Need help?** Check [RAZORPAY_TROUBLESHOOTING.md](./RAZORPAY_TROUBLESHOOTING.md) for detailed debugging
