# Beginner's Guide: How to Use the BTC 15-Minute Arbitrage Bot

Welcome! This guide will walk you through setting up and using the Bitcoin 15-minute arbitrage bot on Polymarket from scratch. No prior experience required!

---

## 📖 Table of Contents

1. [What This Bot Does](#what-this-bot-does)
2. [What You Need Before Starting](#what-you-need-before-starting)
3. [Installation (Step-by-Step)](#installation-step-by-step)
4. [Configuration Setup](#configuration-setup)
5. [Testing Your Setup](#testing-your-setup)
6. [Running the Bot](#running-the-bot)
7. [Understanding the Output](#understanding-the-output)
8. [Common Issues & Solutions](#common-issues--solutions)
9. [Next Steps](#next-steps)

---

## 🎯 What This Bot Does

### In Simple Terms:

This bot automatically finds and executes **guaranteed profit opportunities** on Polymarket's Bitcoin 15-minute markets.

**How it works:**
- Polymarket has markets that ask: "Will Bitcoin go up or down in the next 15 minutes?"
- Each market has two sides: **UP** (Bitcoin goes up) and **DOWN** (Bitcoin goes down)
- At the end of 15 minutes, the winning side pays $1.00 per share
- The bot finds times when you can buy **both sides** for less than $1.00 total
- Since one side will always win, you're guaranteed to make a profit!

### Example:

```
Market prices:
  UP side:   $0.48 per share
  DOWN side: $0.51 per share
  ──────────────────────────
  Total:     $0.99 per share

You buy 5 shares of UP + 5 shares of DOWN = $4.95 invested

At market close (15 minutes later):
  - If UP wins: You get $5.00 back (5 shares × $1.00)
  - If DOWN wins: You get $5.00 back (5 shares × $1.00)
  - Either way, you profit $0.05 (1.01% return in 15 minutes!)
```

**This is called "arbitrage"** - it's a risk-free profit opportunity when markets are temporarily mispriced.

---

## 📋 What You Need Before Starting

Before you begin, make sure you have:

1. ✅ **Python 3.8 or higher** installed on your computer
   - Check by running: `python --version` in your terminal/command prompt
   - Download from: https://www.python.org/downloads/

2. ✅ **A Polymarket account** (free to create)
   - Sign up at: https://polymarket.com/

3. ✅ **USDC funds** in your Polymarket wallet
   - You'll need at least $10-20 to start (recommended: $50-100)
   - Add funds via the Polymarket website

4. ✅ **Your wallet private key** or access to your Polymarket account
   - If you use MetaMask/hardware wallet: You'll need the private key
   - If you use email login (Magic.link): We'll guide you through setup

5. ✅ **Basic terminal/command prompt knowledge**
   - You need to run simple commands (we'll show you exactly what to type)

---

## 🚀 Installation (Step-by-Step)

### Step 1: Download the Bot

**Option A: If you have Git installed:**
```bash
git clone https://github.com/Jonmaa/btc-polymarket-bot.git
cd btc-polymarket-bot
```

**Option B: If you don't have Git:**
1. Go to the GitHub repository
2. Click the green "Code" button
3. Click "Download ZIP"
4. Extract the ZIP file to a folder on your computer
5. Open your terminal/command prompt and navigate to that folder:
   ```bash
   cd path/to/btc-polymarket-bot
   ```

### Step 2: Create a Virtual Environment

This keeps the bot's dependencies separate from other Python projects.

**Windows:**
```bash
python -m venv .venv
.\.venv\Scripts\activate
```

**Mac/Linux:**
```bash
python3 -m venv .venv
source .venv/bin/activate
```

You should see `(.venv)` at the start of your command line, meaning the virtual environment is active.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

This will install all the packages the bot needs. Wait for it to complete (may take 1-2 minutes).

---

## ⚙️ Configuration Setup

Now you need to configure the bot with your account information. This is done through a `.env` file.

### Step 1: Create the .env File

Create a new file named `.env` in the bot's main folder (same folder as `README.md`).

**Windows:**
- You can create it with Notepad or any text editor
- Make sure the file is named exactly `.env` (with the dot at the start)
- If Windows hides the extension, name it `.env.` (with a dot at the end)

**Mac/Linux:**
```bash
touch .env
```

### Step 2: Determine Your Wallet Type

**Which type of account do you have?**

- **Option A: MetaMask, Hardware Wallet, or other external wallet**
  - You connected an external wallet to Polymarket
  - Set `POLYMARKET_SIGNATURE_TYPE=0`
  - You'll need your wallet's private key

- **Option B: Email login (Magic.link)**
  - You signed up with email/password
  - Set `POLYMARKET_SIGNATURE_TYPE=1`
  - You'll need your private key AND your Polymarket proxy wallet address

**Don't know which one?**
- Check how you log into Polymarket
- If you click "Connect Wallet" → Option A
- If you enter email/password → Option B

### Step 3: Get Your Private Key

#### For MetaMask/External Wallet Users:

1. Open MetaMask (or your wallet)
2. Click the three dots menu (⋮) next to your account name
3. Click "Account Details"
4. Click "Show Private Key"
5. Enter your password
6. Copy the private key (starts with `0x...`)
7. **⚠️ KEEP THIS SECRET!** Never share it or commit it to GitHub

#### For Email Login (Magic.link) Users:

1. Log into Polymarket with your email
2. Go to your profile settings
3. Look for "Export Private Key" or "Wallet" section
4. Follow Polymarket's instructions to export your key
5. Copy the private key (starts with `0x...`)

**⚠️ Security Warning:**
- Your private key gives FULL control over your funds
- Store it securely (password manager, encrypted file)
- Never share it online or with anyone
- Never commit it to GitHub or public repositories

### Step 4: Get Your Polymarket Proxy Address (Magic.link Users Only)

**Skip this step if you use MetaMask/external wallet (SIGNATURE_TYPE=0).**

If you use email login, you need your Polymarket proxy wallet address:

1. Go to your Polymarket profile: `https://polymarket.com/@YOUR_USERNAME`
2. Find your balance display
3. Click the "Copy address" button (next to your balance)
4. This is your `POLYMARKET_FUNDER` address
5. It should look like: `0x1234567890abcdef...`

**Important:** This is DIFFERENT from your private key's address. This is your proxy wallet where Polymarket stores your funds.

### Step 5: Fill Out the .env File

Open your `.env` file and add the following (replace the example values with your actual values):

```env
# ============================================
# REQUIRED SETTINGS
# ============================================

# Your wallet's private key (starts with 0x)
POLYMARKET_PRIVATE_KEY=0xYOUR_PRIVATE_KEY_HERE

# Wallet type: 0 = MetaMask/hardware wallet, 1 = Email login (Magic.link)
POLYMARKET_SIGNATURE_TYPE=1

# For Magic.link users ONLY: Your Polymarket proxy wallet address
# For MetaMask users: Leave this EMPTY (or delete this line)
POLYMARKET_FUNDER=0xYOUR_PROXY_WALLET_ADDRESS_HERE

# API credentials (we'll generate these in the next step - leave empty for now)
POLYMARKET_API_KEY=
POLYMARKET_API_SECRET=
POLYMARKET_API_PASSPHRASE=

# ============================================
# TRADING SETTINGS (Recommended for beginners)
# ============================================

# Start in simulation mode (true = safe testing, false = real money)
DRY_RUN=true

# Starting balance for simulation (use any amount, e.g., 100)
SIM_BALANCE=100

# Maximum cost to trigger arbitrage (0.99 = 1% profit, 0.995 = 0.5% profit)
TARGET_PAIR_COST=0.99

# Number of shares to buy per trade (minimum is 5, start small!)
ORDER_SIZE=5

# Order type (FOK = Fill or Kill, safest for beginners)
ORDER_TYPE=FOK

# Seconds to wait between trades (prevents rapid-fire trading)
COOLDOWN_SECONDS=10
```

**Example for MetaMask user:**
```env
POLYMARKET_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
POLYMARKET_SIGNATURE_TYPE=0
POLYMARKET_FUNDER=
DRY_RUN=true
SIM_BALANCE=100
TARGET_PAIR_COST=0.99
ORDER_SIZE=5
ORDER_TYPE=FOK
COOLDOWN_SECONDS=10
```

**Example for Email login user:**
```env
POLYMARKET_PRIVATE_KEY=0x1234567890abcdef1234567890abcdef1234567890abcdef1234567890abcdef
POLYMARKET_SIGNATURE_TYPE=1
POLYMARKET_FUNDER=0xabcdef1234567890abcdef1234567890abcdef1234567890
DRY_RUN=true
SIM_BALANCE=100
TARGET_PAIR_COST=0.99
ORDER_SIZE=5
ORDER_TYPE=FOK
COOLDOWN_SECONDS=10
```

### Step 6: Generate API Keys

The bot needs API credentials to communicate with Polymarket. These are generated from your private key.

1. Make sure your `.env` file has `POLYMARKET_PRIVATE_KEY` filled in
2. Make sure your virtual environment is activated (you should see `(.venv)` in your terminal)
3. Run this command:

```bash
python -m src.generate_api_key
```

You should see output like:
```
API Key: abc123def456...
Secret: xyz789uvw012...
Passphrase: mypassphrase123
```

4. **Copy these three values** and add them to your `.env` file:

```env
POLYMARKET_API_KEY=abc123def456...
POLYMARKET_API_SECRET=xyz789uvw012...
POLYMARKET_API_PASSPHRASE=mypassphrase123
```

**Important:** These API keys are tied to your private key. If you change your private key, you'll need to regenerate these.

---

## 🧪 Testing Your Setup

Before running the bot with real money, let's verify everything is configured correctly.

### Test 1: Check Your Balance

This verifies the bot can connect to your Polymarket account:

```bash
python -m src.test_balance
```

**What you should see:**
- ✓ marks for all configuration items
- Your wallet address
- Your USDC balance (should match what you see on Polymarket)

**If you see errors:**
- "Invalid signature" → Check your `POLYMARKET_FUNDER` (for Magic.link users)
- "Private key not found" → Make sure `POLYMARKET_PRIVATE_KEY` is in your `.env` file
- "Balance: $0.00" but you have funds → Check `POLYMARKET_SIGNATURE_TYPE` and `POLYMARKET_FUNDER`

### Test 2: Diagnose Configuration (If Test 1 Failed)

If you got errors, run the diagnostic tool:

```bash
python -m src.diagnose_config
```

This will check:
- ✅ All environment variables are set correctly
- ✅ Your wallet type matches your configuration
- ✅ Your balance is accessible
- ✅ API connection works

**Common fixes:**
- **"POLYMARKET_FUNDER must be set for Magic.link accounts"**
  → You're using email login but forgot to set `POLYMARKET_FUNDER`
  → Go back to Step 4 and get your proxy wallet address

- **"POLYMARKET_FUNDER equals your signer address"**
  → You set `POLYMARKET_FUNDER` to your private key's address instead of your Polymarket proxy address
  → Get the correct address from your Polymarket profile page

---

## 🤖 Running the Bot

### First Time: Run in Simulation Mode (RECOMMENDED)

**Always test in simulation mode first!** This lets you see how the bot works without risking real money.

1. **Make sure `DRY_RUN=true` in your `.env` file**

2. **Run the bot:**
```bash
python -m src.simple_arb_bot
```

3. **What you'll see:**
   - Bot starts up and finds the current BTC 15-minute market
   - It continuously scans for arbitrage opportunities
   - When it finds one, it shows the details but doesn't actually trade
   - Watch it run for a few minutes to understand the behavior

4. **To stop the bot:**
   - Press `Ctrl+C` (Windows/Linux) or `Cmd+C` (Mac)

### Understanding the Output

Here's what the bot's output means:

```
🚀 BITCOIN 15MIN ARBITRAGE BOT STARTED
======================================================================
Market: btc-updown-15m-1765301400
Time remaining: 12m 34s
Mode: 🔸 SIMULATION                    ← You're in safe mode
Cost threshold: $0.99
Order size: 5 shares
======================================================================

[Scan #1] 12:34:56
No arbitrage: UP=$0.48 (100) + DOWN=$0.52 (150) = $1.00 (threshold=$0.99)
                                                      ↑ Total price
                                                           ↑ Your threshold
```

**When an opportunity is found:**
```
🎯 ARBITRAGE OPPORTUNITY DETECTED
======================================================================
UP limit price:       $0.4800
DOWN limit price:     $0.5100
Total cost:           $0.9900
Profit per share:     $0.0100
Profit %:             1.01%
----------------------------------------------------------------------
Order size:           5 shares each side
Total investment:     $4.95
Expected payout:      $5.00
EXPECTED PROFIT:      $0.05
======================================================================
🔸 SIMULATION MODE - No real orders will be executed
💰 Simulated balance: $95.05 (after deducting $4.95)
```

### Going Live: Real Trading

**⚠️ WARNING: Only do this after testing in simulation mode!**

1. **Make sure you have USDC in your Polymarket wallet** (at least $20-50 recommended)

2. **Change `DRY_RUN=false` in your `.env` file:**
```env
DRY_RUN=false
```

3. **Run the bot:**
```bash
python -m src.simple_arb_bot
```

4. **Watch carefully:**
   - Mode should show: `🔴 REAL TRADING`
   - The bot will now place actual orders on Polymarket
   - Monitor your Polymarket account to see trades executing
   - Start with small `ORDER_SIZE` (5 shares) to minimize risk

5. **At market close (every 15 minutes):**
   - The bot shows a summary of all trades
   - Your profits are automatically credited to your Polymarket account
   - The bot automatically switches to the next 15-minute market

---

## 📊 Understanding the Output

### Key Terms Explained

- **Market:** Each 15-minute period is a separate market (e.g., `btc-updown-15m-1765301400`)
- **Time remaining:** How long until the current market closes
- **UP/DOWN prices:** The current cost to buy one share of each side
- **Total cost:** UP price + DOWN price (needs to be < $1.00 for profit)
- **Order size:** Number of shares you're buying of each side
- **Expected profit:** How much profit you'll make if the trade executes

### What Happens During Trading

1. **Scanning:** Bot continuously checks prices (every few seconds)
2. **Detection:** When UP + DOWN < threshold, opportunity is found
3. **Execution:** Bot places orders to buy both sides simultaneously
4. **Verification:** Bot confirms both orders filled successfully
5. **Waiting:** Bot waits for market to close (every 15 minutes)
6. **Payout:** Winning side pays $1.00 per share automatically

### Final Summary (After Market Closes)

```
🏁 MARKET CLOSED - FINAL SUMMARY
======================================================================
Market: btc-updown-15m-1765301400
Result: UP (goes up) 📈
Mode: 🔴 REAL TRADING
----------------------------------------------------------------------
Total opportunities detected:   3
Total trades executed:          3
Total shares bought:            30
----------------------------------------------------------------------
Total invested:                 $14.85
Expected payout at close:       $15.00
Expected profit:                $0.15 (1.01%)
======================================================================
```

---

## 🔧 Common Issues & Solutions

### Issue 1: "Invalid signature" Error

**Symptoms:**
- Bot fails to connect
- Error message mentions "signature" or "authentication"

**Solutions:**
1. **For Magic.link users:** Make sure `POLYMARKET_FUNDER` is set to your Polymarket proxy address (not your private key's address)
2. **Regenerate API keys:** Run `python -m src.generate_api_key` again
3. **Check signature type:** Verify `POLYMARKET_SIGNATURE_TYPE` matches your account type (0 for MetaMask, 1 for email login)
4. **Run diagnostics:** `python -m src.diagnose_config` for detailed checks

### Issue 2: Balance Shows $0.00

**Symptoms:**
- `test_balance` shows $0.00 but you have funds on Polymarket

**Solutions:**
1. **For Magic.link users:** Set `POLYMARKET_FUNDER` to your proxy wallet address
2. **Check wallet connection:** Make sure your private key matches the wallet with funds
3. **Verify on Polymarket:** Check your balance at polymarket.com matches what you expect

### Issue 3: "No active BTC 15min market found"

**Symptoms:**
- Bot can't find a market to trade

**Solutions:**
1. **Wait a moment:** Markets open every 15 minutes, wait for the next one
2. **Check internet:** Make sure you're connected to the internet
3. **Manual check:** Visit https://polymarket.com/crypto/15M to see if markets are available

### Issue 4: Bot Runs But Finds No Opportunities

**Symptoms:**
- Bot scans continuously but never executes trades

**This is normal!** Arbitrage opportunities are rare. The bot will execute when:
- Market prices create a gap (UP + DOWN < your threshold)
- There's enough liquidity (sellers available)
- You have sufficient balance

**To increase chances:**
- Lower `TARGET_PAIR_COST` (e.g., 0.995 instead of 0.99) - but this reduces profit per trade
- Wait during volatile market conditions (more price gaps occur)
- Increase `ORDER_SIZE` (but this requires more capital)

### Issue 5: "Insufficient balance" Error

**Symptoms:**
- Bot detects opportunity but can't execute

**Solutions:**
1. **Add more USDC** to your Polymarket wallet
2. **Reduce `ORDER_SIZE`** (try 5 instead of higher values)
3. **Check your balance:** Run `python -m src.test_balance` to verify available funds

### Issue 6: One Leg Filled, Other Didn't (Partial Fill)

**Symptoms:**
- Bot shows "Partial fill detected" warning

**What happens:**
- The bot automatically tries to cancel the unfilled order
- It attempts to sell the filled leg to minimize risk
- This is a safety feature, but you may incur a small loss

**Prevention:**
- Use `ORDER_TYPE=FOK` (Fill or Kill) - ensures both legs fill or neither does
- Lower `ORDER_SIZE` if this happens frequently (not enough liquidity)

---

## 📈 Next Steps

### After Successful Testing

1. ✅ **Start small:** Keep `ORDER_SIZE=5` for your first real trades
2. ✅ **Monitor closely:** Watch the bot's first few real trades
3. ✅ **Check Polymarket:** Verify trades appear in your account
4. ✅ **Review profits:** After markets close, check your balance increased

### Optimizing Performance

Once comfortable, you can adjust settings:

**Increase profit per trade:**
- Lower `TARGET_PAIR_COST` (e.g., 0.985) - but fewer opportunities

**Increase trade frequency:**
- Raise `TARGET_PAIR_COST` (e.g., 0.995) - more opportunities, less profit each

**Trade larger sizes:**
- Increase `ORDER_SIZE` (e.g., 10, 20, 50) - requires more capital

**Faster execution:**
- Enable WebSocket mode (set `USE_WSS=true` in `.env`) - lower latency

### Safety Tips

- ⚠️ **Never invest more than you can afford to lose**
- ⚠️ **Start with simulation mode** until you understand the bot
- ⚠️ **Monitor your first real trades** closely
- ⚠️ **Keep your private key secure** - never share it
- ⚠️ **Markets are volatile** - arbitrage opportunities come and go quickly
- ⚠️ **This is not financial advice** - trade at your own risk

### Getting Help

If you encounter issues:

1. **Check the diagnostics:** Run `python -m src.diagnose_config`
2. **Review the main README:** More detailed technical documentation
3. **Check your configuration:** Compare your `.env` file with examples in this guide
4. **Verify your account:** Make sure you can trade manually on Polymarket first

---

## 🎉 Congratulations!

You've successfully set up and are running the BTC 15-minute arbitrage bot! 

Remember:
- ✅ Always test in simulation mode first
- ✅ Start with small order sizes
- ✅ Monitor your trades
- ✅ Keep your private key secure
- ✅ Trade responsibly

Happy trading! 🚀

---

## 📚 Quick Reference: Commands

```bash
# Activate virtual environment (Windows)
.\.venv\Scripts\activate

# Activate virtual environment (Mac/Linux)
source .venv/bin/activate

# Generate API keys
python -m src.generate_api_key

# Test your balance
python -m src.test_balance

# Diagnose configuration issues
python -m src.diagnose_config

# Run bot in simulation mode
python -m src.simple_arb_bot

# Stop the bot
Ctrl+C (Windows/Linux) or Cmd+C (Mac)
```

---

**Last Updated:** 2024
**Bot Version:** 15-minute BTC Arbitrage Bot
**For more details, see:** README.md
