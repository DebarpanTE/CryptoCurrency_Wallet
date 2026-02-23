# COMPLETE TESTING GUIDE - ALL FEATURES

## 🎯 How to Test Each Feature Step-by-Step

---

## 📋 TESTING CHECKLIST

- [ ] 1. Create Wallet
- [ ] 2. Access Wallet
- [ ] 3. Send Transaction
- [ ] 4. QR Code Generation
- [ ] 5. Export CSV
- [ ] 6. Export PDF
- [ ] 7. Enable 2FA
- [ ] 8. Verify 2FA
- [ ] 9. Wallet Backup
- [ ] 10. Restore Wallet
- [ ] 11. Exchange Rates
- [ ] 12. Real-time Updates
- [ ] 13. Multi-signature Wallet (API)

---

## 🧪 TEST 1: CREATE NEW WALLET

### Steps:

1. **Open:** http://localhost:5000
2. **Click:** "Create Wallet" button (blue button)
3. **Wait:** Modal appears with wallet info

### Expected Results:

```
✅ Modal appears with title: "Wallet Created Successfully!"
✅ Shows Wallet Address (starts with 0x...)
✅ Shows Private Key (64 characters)
✅ Shows Initial Balance: 1000 COIN
✅ Shows "Next Steps" section
✅ "Copy Private Key" button works
✅ "Go to Wallet" button present
```

### Sample Output:

```
Wallet Address:
0x1a2b3c4d5e6f7g8h9i0j1k2l3m4n5o6p7q8r9s0t

Private Key:
a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6q7r8s9t0u1v2w3x4y5z6a7b8c9d0e1f2

Initial Balance:
1000 COIN
```

### What to Save:

```
📝 SAVE THESE IN NOTEPAD:
Address: [copy the full address]
Private Key: [copy the full private key]
```

**Status:** ✅ PASS if modal shows all information

---

## 🧪 TEST 2: ACCESS EXISTING WALLET

### Prerequisites:

- Have created a wallet in Test 1
- Saved the address and private key

### Steps:

1. **Open:** http://localhost:5000
2. **In "Access Existing Wallet" card:**
   - Paste your wallet address in "Wallet Address" field
   - Paste your private key in "Private Key" field
3. **Click:** "Access Wallet" (green button)
4. **Wait:** Should redirect to wallet dashboard

### Test Data:

```
Wallet Address: [paste from Test 1]
Private Key: [paste from Test 1]
```

### Expected Results:

```
✅ Page redirects to /wallet/0x...
✅ Shows your wallet address at top
✅ Shows "Current Balance: 1000"
✅ Shows "Real-time updates enabled" indicator
✅ Shows Quick Stats (Total Transactions: 0)
✅ Shows Enhanced Features panel (6 buttons)
✅ Shows Send Transaction form
✅ Shows Recent Transactions (empty for now)
```

**Status:** ✅ PASS if wallet dashboard loads

---

## 🧪 TEST 3: SEND TRANSACTION

### Prerequisites:

- Have 2 wallets created (Alice and Bob)
- Accessed Alice's wallet

### Steps:

#### Step 3.1: Create Second Wallet (Bob)

1. Open new browser tab: http://localhost:5000
2. Click "Create Wallet"
3. Save Bob's address and private key

#### Step 3.2: Send from Alice to Bob

1. Go back to Alice's wallet tab
2. In "Send Cryptocurrency" form:
   - **Recipient Address:** [Bob's address]
   - **Amount:** 250
   - **Your Private Key:** [Alice's private key]
3. Click "Send Transaction"

### Test Data Example:

```
From: Alice's wallet (0x1a2b...)
To: Bob's address (0x9z8y...)
Amount: 250
Private Key: [Alice's private key]
```

### Expected Results:

```
✅ Green notification: "Transaction sent successfully! ✅"
✅ Form clears automatically
✅ Recent Transactions updates (shows sent -250)
✅ Balance updates to 750 (1000 - 250)
✅ Transaction appears with 📤 icon (red amount)
```

#### Step 3.3: Verify Bob Received

1. Access Bob's wallet (new tab)
2. Check balance

### Expected for Bob:

```
✅ Balance shows: 1250 (1000 + 250)
✅ Recent Transactions shows received +250
✅ Transaction with 📥 icon (green amount)
```

**Status:** ✅ PASS if both wallets update correctly

---

## 🧪 TEST 4: QR CODE GENERATION

### Prerequisites:

- Accessed a wallet

### Steps:

1. **In wallet dashboard**
2. **Click:** "📱 Show QR Code" button
3. **Wait:** Modal appears with QR code

### Expected Results:

```
✅ Modal opens with title: "Your Wallet QR Code"
✅ QR code image displayed (black and white squares)
✅ Wallet address shown below QR code
✅ "Copy Address" button present
✅ QR code can be scanned with phone camera
✅ Close button (×) works
```

### How to Verify QR Code:

```
1. Use phone camera or QR scanner app
2. Scan the QR code
3. Should show your wallet address
```

**Status:** ✅ PASS if QR code displays and scans correctly

---

## 🧪 TEST 5: EXPORT TO CSV

### Prerequisites:

- Have at least 1 transaction (from Test 3)

### Steps:

1. **In wallet dashboard**
2. **Click:** "📄 Export CSV" button
3. **Wait:** File downloads

### Expected Results:

```
✅ Browser downloads a CSV file
✅ Filename: transactions_0x1a2b..._20260211_123456.csv
✅ File contains transaction data
✅ Can open in Excel/Google Sheets
```

### CSV Content Should Show:

```csv
Date,Type,From,To,Amount,Transaction Hash,Status
2026-02-11 12:30:00,Sent,0x1a2b...,0x9z8y...,250,a1b2c3...,completed
```

### Verify in Excel:

```
✅ Opens without errors
✅ 7 columns (Date, Type, From, To, Amount, Hash, Status)
✅ Transaction data is correct
✅ Amount matches what you sent
```

**Status:** ✅ PASS if CSV downloads and opens correctly

---

## 🧪 TEST 6: EXPORT TO PDF

### Prerequisites:

- Have at least 1 transaction

### Steps:

1. **In wallet dashboard**
2. **Click:** "📑 Export PDF" button
3. **Wait:** PDF downloads

### Expected Results:

```
✅ Browser downloads a PDF file
✅ Filename: transactions_0x1a2b..._20260211_123456.pdf
✅ PDF opens in PDF viewer
✅ Professional formatting
```

### PDF Should Contain:

```
✅ Title: "Transaction History Report"
✅ Wallet Address
✅ Current Balance
✅ Report Generated timestamp
✅ Total Transactions count
✅ Transaction table with:
   - Date
   - Type (Sent/Received)
   - Amount (with +/-)
   - Transaction hash
   - Status
```

**Status:** ✅ PASS if PDF downloads and displays correctly

---

## 🧪 TEST 7: ENABLE TWO-FACTOR AUTHENTICATION

### Prerequisites:

- Accessed a wallet
- Have authenticator app installed (Google Authenticator, Authy, etc.)

### Steps:

1. **In wallet dashboard**
2. **Click:** "🔐 Enable 2FA" button
3. **Wait:** Modal appears with QR code

### Expected Results:

```
✅ Modal opens: "Enable Two-Factor Authentication"
✅ QR code displayed
✅ Secret key shown (example: JBSWY3DPEHPK3PXP)
✅ Warning message: "⚠️ Save this secret key in a safe place!"
✅ Can close modal (×)
```

### How to Test:

```
Step 1: Open authenticator app on phone
Step 2: Click "Add Account" or "+"
Step 3: Scan the QR code
Step 4: App shows 6-digit code (changes every 30 seconds)
```

### Authenticator App Should Show:

```
CryptoWallet (0x1a2b...)
123 456  ← Changes every 30 seconds
```

### Save This Info:

```
📝 Secret Key: [copy and save safely]
This can restore 2FA if you lose your phone
```

**Status:** ✅ PASS if QR code scans and appears in authenticator app

---

## 🧪 TEST 8: VERIFY 2FA TOKEN

### Prerequisites:

- Completed Test 7 (2FA enabled)
- Have authenticator app with codes

### Steps:

1. **Open browser console** (F12)
2. **Type this JavaScript:**

```javascript
fetch("/verify_2fa", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    address: "YOUR_WALLET_ADDRESS",
    token: "123456", // Replace with current code from app
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

3. **Replace:**
   - `YOUR_WALLET_ADDRESS` with your actual address
   - `123456` with the 6-digit code from authenticator app

### Expected Results:

```javascript
✅ Console shows:
{
    success: true,
    valid: true  // If code is correct
}

OR

{
    success: true,
    valid: false  // If code is wrong/expired
}
```

### Test Cases:

```
Test 1: Use current code → valid: true ✅
Test 2: Use old code (expired) → valid: false ✅
Test 3: Use random numbers → valid: false ✅
```

**Status:** ✅ PASS if correct codes validate

---

## 🧪 TEST 9: WALLET BACKUP

### Prerequisites:

- Accessed a wallet

### Steps:

1. **In wallet dashboard**
2. **Click:** "💾 Backup Wallet" button
3. **Enter password:** (Example: "MySecurePassword123")
4. **Click OK**
5. **Wait:** Modal appears with mnemonic phrase

### Expected Results:

```
✅ Modal opens: "⚠️ SAVE YOUR BACKUP PHRASE!"
✅ Shows 12-word mnemonic phrase
✅ Words separated by spaces
✅ Yellow warning box
✅ Red warning text about saving it
✅ "Copy to Clipboard" button works
```

### Sample Mnemonic:

```
abandon ability able about above absent absorb abstract absurd abuse access accident
```

### What to Do:

```
📝 CRITICAL - SAVE THIS MNEMONIC:
1. Click "Copy to Clipboard"
2. Paste into secure notepad
3. Write it down on paper
4. Store in safe place

⚠️ This is the ONLY way to recover your wallet!
Never share with anyone!
```

### Verify:

```
✅ Exactly 12 words
✅ All lowercase
✅ Separated by spaces
✅ Can copy to clipboard
```

**Status:** ✅ PASS if mnemonic displays and can be copied

---

## 🧪 TEST 10: RESTORE WALLET

### Prerequisites:

- Have a mnemonic phrase from Test 9

### Steps:

1. **Go to:** http://localhost:5000
2. **Click:** "Restore from Backup" button (third card)
3. **In modal:**
   - **Mnemonic Phrase:** [paste your 12 words]
   - **Password:** [same password used in Test 9]
4. **Click:** "Restore Wallet"

### Test Data:

```
Mnemonic: abandon ability able about above absent absorb abstract absurd abuse access accident
Password: MySecurePassword123
```

### Expected Results:

```
✅ Success message appears
✅ Shows: "Mnemonic Validated!"
✅ Shows: "Your backup phrase is valid with 12 words"
✅ Green success alert
```

### Error Tests:

```
Test with wrong word count (11 words):
❌ Error: "Invalid mnemonic phrase length"

Test with invalid password:
❌ Error: "Decryption failed" (if stored)

Test with random words:
⚠️ Warning: "Word 'xyz' not in word list"
```

**Status:** ✅ PASS if valid mnemonic is accepted

---

## 🧪 TEST 11: EXCHANGE RATES

### Prerequisites:

- Accessed a wallet

### Steps:

1. **In wallet dashboard**
2. **Click:** "💱 Exchange Rates" button
3. **Wait:** Modal appears

### Expected Results:

```
✅ Modal opens: "💱 Exchange Rates"
✅ Title: "Exchange Rates (1 COIN =)"
✅ Shows rates for multiple currencies
✅ Formatted nicely in grid
```

### Should Display:

```
BTC
0.000025

ETH
0.000400

USD
1.000000

USDT
1.000000
```

### Verify:

```
✅ All currencies shown (BTC, ETH, USD, USDT)
✅ Rates are numbers (not errors)
✅ Formatted with 6 decimal places
✅ Modal closes with × button
```

**Status:** ✅ PASS if exchange rates display

---

## 🧪 TEST 12: REAL-TIME UPDATES (WebSocket)

### Prerequisites:

- Have 2 wallets (Alice and Bob)

### Steps:

#### Setup:

1. **Browser 1:** Access Alice's wallet
2. **Browser 2:** Access Alice's wallet (same address)
3. **Arrange windows side-by-side**

#### Test:

1. **In Browser 1:** Send transaction to Bob (250 coins)
2. **Watch Browser 2:** Should update automatically

### Expected Results:

**Browser 1 (Sender):**

```
✅ Transaction sent notification
✅ Balance updates: 1000 → 750
✅ Transaction appears in list
```

**Browser 2 (Real-time):**

```
✅ Green notification: "Balance updated in real-time! 🔄"
✅ Balance number changes: 1000 → 750
✅ Blue notification: "New transaction received! 💰"
✅ Transaction list refreshes
✅ All without page reload!
```

### Visual Check:

```
✅ Real-time indicator shows: "⚡ Real-time updates enabled"
✅ Green pulsing dot next to indicator
✅ Updates happen within 1-2 seconds
```

### Browser Console Check:

```javascript
F12 → Console tab
Should see:
✅ "WebSocket connected"
✅ "Balance update received"
✅ "New transaction received"
```

**Status:** ✅ PASS if Browser 2 updates without refresh

---

## 🧪 TEST 13: MULTI-SIGNATURE WALLET (API)

### Prerequisites:

- Have 3 wallets created (Owner1, Owner2, Owner3)
- Know their addresses

### Steps:

#### Using Browser Console (F12):

```javascript
// Create multisig wallet requiring 2 of 3 signatures
fetch("/create_multisig", {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    owners: [
      "0x1a2b...", // Owner1 address
      "0x9z8y...", // Owner2 address
      "0x5t6u...", // Owner3 address
    ],
    required_signatures: 2,
  }),
})
  .then((res) => res.json())
  .then((data) => console.log(data));
```

### Expected Results:

```javascript
✅ Console shows:
{
    success: true,
    message: "Multi-signature wallet created successfully",
    data: {
        address: "0xMULTISIG...",
        balance: 1000,
        is_multisig: true,
        required_signatures: 2,
        owners: ["0x1a2b...", "0x9z8y...", "0x5t6u..."],
        created_at: "2026-02-11T12:30:00"
    }
}
```

### Verify:

```
✅ New multisig address created
✅ Has 3 owners
✅ Requires 2 signatures
✅ Has initial balance
```

**Status:** ✅ PASS if multisig wallet created

---

## 📊 COMPLETE TESTING MATRIX

| #   | Feature          | Test Method | Expected Result        | Status |
| --- | ---------------- | ----------- | ---------------------- | ------ |
| 1   | Create Wallet    | UI Button   | Modal with address/key | ⬜     |
| 2   | Access Wallet    | UI Form     | Dashboard loads        | ⬜     |
| 3   | Send Transaction | UI Form     | Balance updates        | ⬜     |
| 4   | QR Code          | UI Button   | QR displays            | ⬜     |
| 5   | Export CSV       | UI Button   | CSV downloads          | ⬜     |
| 6   | Export PDF       | UI Button   | PDF downloads          | ⬜     |
| 7   | Enable 2FA       | UI Button   | QR code shows          | ⬜     |
| 8   | Verify 2FA       | API Call    | Token validates        | ⬜     |
| 9   | Backup           | UI Button   | Mnemonic shows         | ⬜     |
| 10  | Restore          | UI Form     | Validates phrase       | ⬜     |
| 11  | Exchange Rates   | UI Button   | Rates display          | ⬜     |
| 12  | Real-time        | 2 Browsers  | Auto-updates           | ⬜     |
| 13  | Multisig         | API Call    | Wallet created         | ⬜     |

---

## 🎯 QUICK TEST SEQUENCE

### 5-Minute Quick Test:

```
1. Create Wallet → ✅ Save address & key
2. Access Wallet → ✅ Dashboard loads
3. Click "Show QR Code" → ✅ QR appears
4. Click "Export CSV" → ✅ Downloads
5. Click "Enable 2FA" → ✅ QR shows
6. Click "Exchange Rates" → ✅ Rates display
7. Click "Backup Wallet" → ✅ Mnemonic shows
```

If all 7 steps work: **✅ Basic features working!**

### 15-Minute Full Test:

```
1. Create 2 wallets (Alice & Bob)
2. Access Alice's wallet
3. Send 250 to Bob
4. Test all 6 enhanced feature buttons
5. Open Alice's wallet in 2 browsers
6. Send transaction in Browser 1
7. Watch Browser 2 update in real-time
```

If all work: **✅ All features working perfectly!**

---

## ❌ COMMON ERRORS & FIXES

### Error: "Wallet not found"

**Fix:** Make sure you're using the EXACT address and private key from wallet creation

### Error: "Insufficient balance"

**Fix:** Check current balance before sending

### Error: "Invalid credentials"

**Fix:** Copy-paste address and key carefully (no extra spaces)

### QR Code doesn't appear:

**Fix:** Check browser console (F12) for errors

### CSV/PDF doesn't download:

**Fix:** Check if browser is blocking downloads

### 2FA QR won't scan:

**Fix:** Increase screen brightness, try different authenticator app

### Real-time updates not working:

**Fix:** Check console for "WebSocket connected" message

---

## ✅ SUCCESS CRITERIA

Your wallet is working perfectly if:

1. ✅ Can create new wallets
2. ✅ Can access existing wallets
3. ✅ Can send transactions
4. ✅ QR codes generate
5. ✅ CSV/PDF exports work
6. ✅ 2FA can be enabled
7. ✅ Wallet can be backed up
8. ✅ Mnemonic can be validated
9. ✅ Exchange rates display
10. ✅ Real-time updates work

**If all 10 work: 🎉 PERFECT! All features operational!**

---

## 📝 TEST RESULTS TEMPLATE

```
Date: ___________
Tester: ___________

TEST RESULTS:
[ ] Create Wallet - PASS/FAIL
[ ] Access Wallet - PASS/FAIL
[ ] Send Transaction - PASS/FAIL
[ ] QR Code - PASS/FAIL
[ ] Export CSV - PASS/FAIL
[ ] Export PDF - PASS/FAIL
[ ] Enable 2FA - PASS/FAIL
[ ] Wallet Backup - PASS/FAIL
[ ] Restore Wallet - PASS/FAIL
[ ] Exchange Rates - PASS/FAIL
[ ] Real-time Updates - PASS/FAIL
[ ] Multisig (API) - PASS/FAIL

Overall Status: PASS/FAIL
```

---

## 🎉 CONGRATULATIONS!

If all tests pass, you have successfully implemented and tested:

- ✅ Core wallet functionality
- ✅ All 8 enhancement features
- ✅ Real-time WebSocket updates
- ✅ Export capabilities
- ✅ Security features (2FA, Backup)

**Your cryptocurrency wallet is production-ready!** 🚀
