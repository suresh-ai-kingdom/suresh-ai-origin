# 💰 Step 4: Switch to LIVE Payments (Get Real Money!)

## Current Problem
- ✅ Razorpay configured BUT in **TEST MODE**
- 🧪 Test payments = ₹0 in your bank account
- 💸 Real customers can't pay you real money

---

## Why No Money Yet?

Your current keys:
```
RAZORPAY_KEY_ID=rzp_test_S1UEbDvGtoEcNW  ← TEST KEY (fake money)
RAZORPAY_KEY_SECRET=9PEkKFhFF63j0IeOMBy2xrjJ  ← TEST SECRET
```

**TEST mode** = Practice payments with fake cards. No real money moves.

---

## How to Get LIVE Keys (Real Money!)

### Step 1: Complete Razorpay KYC
🔗 Visit: https://dashboard.razorpay.com/

1. **Login** to your Razorpay account
2. Go to **Settings** (top right)
3. Click **Configuration** → **API Keys**
4. You'll see:
   - ✅ Test Keys (currently using these)
   - 🔒 Live Keys (locked until KYC complete)

### Step 2: Submit Business Details
If "Live Keys" shows 🔒 Locked:

1. Click **"Complete KYC"** or **"Activate Account"**
2. Fill required info:
   - **Business Name**: Suresh AI Origin (or your registered name)
   - **Business Type**: Individual / Sole Proprietorship / Company
   - **PAN Card**: Your business/personal PAN
   - **Bank Account**: Where you want money deposited
   - **Address Proof**: Aadhaar/Passport/Utility bill

3. **Submit Documents**:
   - PAN card photo
   - Bank statement/cancelled cheque
   - Address proof
   - Business registration (if company)

4. **Wait for Approval** (1-3 business days)
   - Razorpay team reviews
   - You'll get email: "Account Activated"

### Step 3: Generate LIVE Keys
Once approved:

1. Go back to **Settings** → **API Keys**
2. Under **"Live Mode"**, click **"Generate Live Keys"**
3. You'll get:
   ```
   Key ID: rzp_live_XXXXXXXXXXXX
   Key Secret: YYYYYYYYYYYYYYYY (save this!)
   ```
4. ⚠️ **SAVE SECRET NOW** - Can't view again!

---

## Update Your App with LIVE Keys

### Option A: Local Testing (.env file)
```bash
# OLD (Test mode - fake money):
RAZORPAY_KEY_ID=rzp_test_S1UEbDvGtoEcNW
RAZORPAY_KEY_SECRET=9PEkKFhFF63j0IeOMBy2xrjJ

# NEW (Live mode - real money):
RAZORPAY_KEY_ID=rzp_live_YOUR_LIVE_KEY_HERE
RAZORPAY_KEY_SECRET=YOUR_LIVE_SECRET_HERE
```

### Option B: Render Production (Recommended)
**Render Dashboard → Your Service → Environment:**

1. Find `RAZORPAY_KEY_ID`, click **Edit**
2. Replace `rzp_test_...` with `rzp_live_...`
3. Update `RAZORPAY_KEY_SECRET` too
4. Click **Save Changes**
5. App auto-restarts in LIVE mode ✅

---

## Verify LIVE Mode

Run system check:
```powershell
python check_system.py
```

Should show:
```
✅ Razorpay Key ID: Configured
✅ Mode: LIVE (real payments) ← Changed from TEST
```

---

## What Changes with LIVE Mode?

| TEST Mode (Now) | LIVE Mode (After) |
|----------------|-------------------|
| Fake test cards | Real customer cards |
| ₹0 in bank account | Real money deposited |
| Unlimited testing | 2% transaction fee |
| No settlements | T+3 day settlements |
| Demo customers | Real customers |

---

## Transaction Fees (LIVE Mode)

**Razorpay charges:**
- 💳 **2% + ₹0** per transaction
- Example: ₹999 sale → You get ₹979 (₹20 fee)
- No monthly fees, no setup fees

**Your pricing:**
- Starter: ₹99 → You get ~₹97
- Pro: ₹499 → You get ~₹489
- Premium: ₹999 → You get ~₹979

---

## Settlement Timeline (When Money Hits Bank)

1. **Customer pays**: ₹999 on Monday 2 PM
2. **Razorpay holds**: 3 working days (T+3)
3. **You receive**: Thursday ~2 PM in bank account

**First payment might take 5-7 days** as initial verification.

---

## Security Checklist ✅

Before going LIVE:
- [ ] HTTPS enabled on Render (already done ✅)
- [ ] Webhook secret configured (already done ✅)
- [ ] Admin auth enabled (Step 2 ✅)
- [ ] SSL certificate valid (Render auto-manages ✅)
- [ ] Payment confirmation emails working (check Step 2 ✅)

---

## Common Issues

### "Live Keys Not Showing"
→ Complete KYC first. Check email for activation status.

### "Payment Failed in Live Mode"
→ Customer's actual card might be declined. Check Razorpay Dashboard → Payments.

### "Money Not in Bank"
→ Wait T+3 days. Check Razorpay Dashboard → Settlements.

### "Still Shows TEST Mode"
→ Update `.env` on Render, not just local. App needs restart.

---

## Test Your First LIVE Payment

### ⚠️ WARNING: This costs real money!

1. Go to your live site: `https://your-app.onrender.com`
2. Click "Buy Starter Pack" (₹99)
3. Use your **real credit card**
4. Complete payment
5. Check:
   - ✅ Confirmation email received
   - ✅ Download link works
   - ✅ Razorpay Dashboard shows payment
   - ✅ In 3 days, ₹97 in bank (₹99 - ₹2 fee)

---

## Current Status

- ❌ Using TEST keys (fake money)
- ⏳ Waiting for you to get LIVE keys
- 📖 Follow steps above to enable real payments

**Once LIVE keys added:**
```powershell
python check_system.py
# Should show: ✅ Mode: LIVE (real payments) ← 86% health!
```

---

## Need Help?

- 📧 Razorpay Support: https://razorpay.com/support/
- 📞 Call: 1800-102-0555 (India, toll-free)
- 💬 Chat: Dashboard → Help icon (bottom right)

**Next**: Get your LIVE keys and update Render environment variables! 🚀
