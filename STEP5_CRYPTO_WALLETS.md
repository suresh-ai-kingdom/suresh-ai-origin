# ₿ Step 5: Update Crypto Wallet Addresses (Optional)

## Current Status
Your app has crypto payment UI with **DEMO wallet addresses**:
- Bitcoin: `bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh` (demo)
- Ethereum: `0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb` (demo)
- USDT: `TXYZuBkjf5hAcPBH7M9qV8rW3nN2pL5kD9` (demo)
- Solana: `DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK` (demo)

**⚠️ Payments to these addresses won't reach you!**

---

## Do You Need This?

**Skip if:**
- ✅ Razorpay is enough (covers UPI, cards, netbanking)
- ✅ You don't accept crypto yet
- ✅ Target audience doesn't use crypto

**Needed if:**
- 🌍 International customers (crypto easier than cards)
- 🔒 Privacy-focused buyers (no KYC)
- 💰 Large transactions (lower fees than cards)

---

## How to Get Crypto Wallets (FREE)

### Option 1: Trust Wallet (Recommended - Easy)
1. Download: https://trustwallet.com/ (mobile app)
2. Create wallet → Backup seed phrase ⚠️ CRITICAL
3. Get addresses:
   - Tap "Bitcoin" → Tap "Receive" → Copy address
   - Tap "Ethereum" → Tap "Receive" → Copy address
   - Tap "Tether USD" → Tap "Receive" → Copy USDT address
   - Tap "Solana" → Tap "Receive" → Copy address

### Option 2: MetaMask (Web Extension)
1. Install: https://metamask.io/
2. For Ethereum/USDT only
3. Get address: Click account → Copy address

### Option 3: Hardware Wallet (Most Secure)
- Ledger: https://www.ledger.com/ (~₹8,000)
- Trezor: https://trezor.io/ (~₹10,000)
- Best for large amounts (₹1L+)

---

## Update Wallet Addresses in Code

### File: `static/crypto-effects.js` (Line 343)

**Current (DEMO):**
```javascript
const walletAddresses = {
    bitcoin: 'bc1qxy2kgdygjrsqtzq2n0yrf2493p83kkfjhx0wlh',
    ethereum: '0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb',
    usdt: 'TXYZuBkjf5hAcPBH7M9qV8rW3nN2pL5kD9',
    solana: 'DYw8jCTfwHNRJhhmFcbXvVDTqWMEVFBX6ZKUmG5CNSKK'
};
```

**Replace with YOUR addresses:**
```javascript
const walletAddresses = {
    bitcoin: 'YOUR_BTC_ADDRESS_HERE',      // Starts with bc1... or 1... or 3...
    ethereum: 'YOUR_ETH_ADDRESS_HERE',     // Starts with 0x...
    usdt: 'YOUR_USDT_ADDRESS_HERE',        // Tron: T... / Ethereum: 0x...
    solana: 'YOUR_SOL_ADDRESS_HERE'        // Starts with uppercase letters
};
```

### Example with Real Addresses:
```javascript
const walletAddresses = {
    bitcoin: 'bc1q9z8x7y6w5v4t3s2r1q0p9o8n7m6l5k4j3h2g1',
    ethereum: '0x1234567890ABCDEFabcdef1234567890ABCDEF12',
    usdt: 'TR7NHqjeKQxGTCi8q8ZY4pL3kiSrtv9xCd',
    solana: 'ABC123DEF456GHI789JKL012MNO345PQR678STU901'
};
```

---

## Security Best Practices 🔒

### DO:
- ✅ **Backup seed phrase** offline (paper, metal plate)
- ✅ Use hardware wallet for large amounts
- ✅ Test with small amount first (₹100)
- ✅ Verify address character-by-character (one typo = lost forever)
- ✅ Store seed in fireproof safe

### DON'T:
- ❌ Share seed phrase with ANYONE (not even support)
- ❌ Screenshot seed phrase
- ❌ Store seed in cloud/email
- ❌ Use exchange wallet for receiving (not your keys = not your coins)
- ❌ Copy-paste without double-checking (malware can change clipboard)

---

## Test Crypto Payments

1. **Update addresses** in `crypto-effects.js`
2. **Commit and push** to GitHub:
   ```powershell
   git add static/crypto-effects.js
   git commit -m "Update crypto wallet addresses"
   git push
   ```
3. **Wait for Render deploy** (auto-deploys from GitHub)
4. **Test on live site**:
   - Visit: `https://your-app.onrender.com`
   - Click crypto icon (floating button)
   - Select Bitcoin → See YOUR address
   - Send test payment (₹100 worth BTC)
   - Verify it arrives in your wallet

---

## How Customers Pay with Crypto

1. Click **"Pay with Crypto"** button on your site
2. Choose coin (BTC/ETH/USDT/SOL)
3. See YOUR wallet address + QR code
4. Scan QR or copy address
5. Open their crypto wallet
6. Send payment
7. **Manual verification** (you check wallet, then send download link)

### ⚠️ No Auto-Detection Yet
Unlike Razorpay, crypto needs manual verification:
- Customer sends payment
- You check your wallet (Trust Wallet, etc.)
- Once confirmed, you email download link manually

**Future upgrade**: Add blockchain API for auto-confirmation (Alchemy, BlockCypher)

---

## Transaction Fees (Crypto vs Razorpay)

| Payment Method | Fee | Speed | Example (₹999) |
|---------------|-----|-------|----------------|
| **Razorpay** | 2% | Instant | ₹979 (₹20 fee) |
| **Bitcoin** | ~0.5% | 10-60 min | ₹994 (₹5 fee) |
| **Ethereum** | ~1% | 1-5 min | ₹989 (₹10 fee) |
| **USDT (Tron)** | ~₹5 flat | 1-3 min | ₹994 (₹5 fee) |
| **Solana** | ~₹0.50 flat | 5-30 sec | ₹998.50 (₹0.50 fee) |

**Winner**: Solana for small amounts, Bitcoin for large amounts

---

## Current Crypto Status

Run system check:
```powershell
python check_system.py
```

Shows:
```
⚠️ Using DEMO wallet addresses
   → Update walletAddresses in static/crypto-effects.js
```

After updating:
```powershell
git add static/crypto-effects.js
git commit -m "Update to real crypto wallets"
git push
```

Render auto-deploys → Crypto payments go to YOUR wallets ✅

---

## Priority Level: LOW

**Focus on Steps 1-4 first** (database, admin, AI, live payments).

Crypto is **optional** - Razorpay handles 99% of Indian customers.

Add crypto later if you get international users or crypto requests.

---

**Next**: Skip this step for now, or update wallets if you have them ready! 🚀
