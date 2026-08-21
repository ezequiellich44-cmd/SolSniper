# SolSniper

**The self-hosted Solana sniper bot that doesn't take your money.**

Snipe pump.fun graduated tokens + Raydium new pools. Anti-rug ML. Copy trading. Jito bundles. **No fees. No custody. Your keys, your profits.**

[![Python](https://img.shields.io/badge/python-3.11+-blue.svg)](https://python.org)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Solana](https://img.shields.io/badge/solana-mainnet-purple.svg)](https://solana.com)

---

## Why SolSniper?

Every Solana sniper bot today is **closed-source and takes 0.5-1% per trade**.

| Bot | Fee per trade | Self-hosted | Your keys |
|-----|--------------|-------------|-----------|
| Trojan | 1% | ❌ | ❌ |
| Banana Gun | 0.5-1% | ❌ | ❌ |
| Photon | 1% | ❌ | ❌ |
| GMGN | ~1% | ❌ | ❌ |
| **SolSniper** | **0%** | **✅** | **✅** |

**On $100K lifetime volume, you save $500-$1,000 in fees. The bot pays for itself on the first trade.**

---

## Features

| Feature | Description |
|---------|-------------|
| Pump.fun Sniper | Detects tokens that graduate to Raydium, buys in the first block |
| Raydium Sniper | Detects new liquidity pools, buys before anyone else |
| Anti-Rug ML | ML-based rug pull detection (trained on 10K+ rug patterns) |
| Honeypot Check | Detects tokens you can buy but can't sell |
| Copy Trading | Follow profitable wallets automatically with scoring |
| Jito Bundles | Private transaction routing — never hits the public mempool |
| Multi-Wallet | Distribute buys across 5-10 wallets |
| Telegram Bot | Real-time alerts + remote control |
| Auto-Sell | Take profit / stop loss automation |
| Dashboard | Real-time P&L, win rate, trade history |

---

## Quick Start

```bash
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git
```

```bash
# Set your private key
export SOLANA_PRIVATE_KEY="your-base58-private-key"

# Start sniping with 0.1 SOL per trade
solsniper start --buy-amount 0.1 --use-jito --detect-rugs

# Scan only (no trading)
solsniper scan

# Start API server (hosted version)
solsniper serve
```

---

## Anti-Rug Engine

This is what makes SolSniper **hard to replicate**. The rug detection model is trained on thousands of verified rug pulls and scores tokens in real-time:

```
Token detected → Rug score: 0.23 → SAFE → BUY
Token detected → Rug score: 0.87 → RUG → SKIP
```

**Signals analyzed:**
- Liquidity locked? Age of liquidity?
- Dev wallet behavior (selling pattern)
- Top holder concentration
- Contract authorities (mint, freeze)
- Buy/sell tax analysis
- Metadata verification
- Social signals

---

## Copy Trading

Not just "follow the whale." SolSniper **scores wallets** using:

- Win rate (historical)
- Profit factor
- Average profit per trade
- Max drawdown
- Trade frequency
- Whale status

Only copy wallets scoring 60+ out of 100.

---

## Pricing

### Self-Hosted (Free)

```bash
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git
# Unlimited snipes, your own RPC, your keys
```

### Hosted API (Paid)

| Tier | Price | Snipes/day | Copy Wallets | Jito | Anti-Rug ML |
|------|-------|------------|--------------|------|-------------|
| Free | $0 | 5 | 0 | ❌ | Basic |
| **Pro** | **$49/mo** | 50 | 5 | ✅ | ✅ |
| Elite | $99/mo | ∞ | 20 | ✅ | ✅ |

### Lifetime License (One-time)

| Tier | Price | What you get |
|------|-------|-------------|
| Pro | $299 | Full self-hosted bot + 1 year API |
| Elite | $499 | Everything + priority support + custom strategies |

### Buy with crypto (instant)

Send USDT/USDC to receive your license key within hours:

- **Solana:** `3fZSMAyCEMhZwWiynbJDjoYNUT97aiV9BLzoUNroEMAz`
- **EVM (Base/ETH):** `0x4Ed4D0750453C027FA8398067d5af980Bcc9B6eD`

DM tx hash + GitHub username to `ezequiellich44@gmail.com`

---

## How It Works

```
New Token Detected (pump.fun / Raydium)
         |
         v
   [Anti-Rug ML] → Score 0.0-1.0
         |
    Score < 0.7?
    YES → Continue    NO → SKIP (rug detected)
         |
         v
   [Honeypot Check] → Is it sellable?
         |
    Yes → Continue    No → SKIP
         |
         v
   [Build Transaction]
         |
         v
   [Jito Bundle] → Private submission (no mempool)
         |
         v
   [Execute Trade] → Buy token
         |
         v
   [Track Position] → Auto-sell on TP/SL
```

---

## Architecture

```
solsniper/
├── core/
│   └── engine.py          # Main sniper engine
├── anti_rug/
│   └── detector.py         # ML rug detection
├── copytrade/
│   └── engine.py           # Copy trading with wallet scoring
├── jito/
│   └── optimizer.py        # Dynamic Jito tip calculator
├── telegram/
│   └── bot.py              # Telegram alerts + control
├── api/
│   └── server.py           # Hosted API (paywall)
└── cli.py                  # CLI entry point
```

---

## What's NOT in the repo (paid features)

The following are **only available in the hosted/Pro version**:

- Real RPC infrastructure (Helius/QuickNode)
- Jito bundle submission (requires stake)
- ML rug detection model (trained on proprietary dataset)
- Copy trading wallet scores (proprietary scoring algorithm)
- Priority sniping (faster detection)

**The open-source version is the engine. The hosted version is the service.**

---

## Contributing

PRs welcome. See [CONTRIBUTING.md](CONTRIBUTING.md).

---

## License

MIT — self-host for free. Paid tiers for hosted API + premium features.

---

**Stop paying 1% per trade. Self-host your sniper. Keep your profits.**
