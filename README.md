# SolSniper - The Most Advanced Solana Trading Bot

<p align="center">
  <strong>AI-Powered Rug Detection + Auto Trading + Smart Money Tracking</strong><br>
  The only bot that protects you AND makes you money.
</p>

<p align="center">
  <a href="https://ezequiellich44-cmd.github.io/SolSniper/"><img src="https://img.shields.io/badge/Landing%20Page-Live-brightgreen" alt="Landing Page"></a>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper/actions"><img src="https://github.com/ezequiellich44-cmd/SolSniper/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
</p>

---

## Why SolSniper?

**80% of new Solana tokens are rug pulls.** Every day, traders lose millions. Existing bots like Trojan (1% fee), Banana Gun (0.5% fee), and Photon (1% fee) charge you but offer ZERO anti-rug protection.

**SolSniper is different:**
- **0% trading fees** - Keep 100% of profits
- **AI-powered rug detection** - Real ML, not pattern matching
- **Token scoring 0.0-1.0** - Know the risk before you trade
- **Auto trading** - Set TP/SL, bot executes automatically
- **Smart money tracking** - See what whales are buying
- **Self-hosted** - Your keys, your control
- **Open source** - Full transparency

## Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **AI Rug Detection** | ML engine analyzes 50+ on-chain signals | Avoid rug pulls before they happen |
| **Token Scoring** | Real-time risk score 0.0-1.0 | Make informed decisions instantly |
| **Auto Trading** | Take-profit, stop-loss, trailing stop | Maximize profits, minimize losses |
| **Smart Money** | Track top wallets in real-time | Copy successful traders |
| **Token Discovery** | Find trending tokens, new launches | Never miss an opportunity |
| **Jito Bundles** | Private mempool execution | No front-running, no sandwiches |
| **0% Fees** | Zero trading fees | Keep 100% of your profits |
| **Self-Hosted** | Run on your own server | Full control, full transparency |

## Quick Start

`ash
# Install
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git

# Scan a token
solsniper scan <TOKEN_ADDRESS>

# Start the bot
solsniper start

# Run demo
solsniper demo
`

## How It Works

### 1. AI Rug Detection
`python
from solsniper.ai_rug_detector import AdvancedRugDetector

detector = AdvancedRugDetector()
analysis = await detector.analyze(token_address)

print(f"Risk Score: {analysis.risk_score}/1.0")
print(f"Risk Level: {analysis.risk_level}")
print(f"Confidence: {analysis.confidence}%")
`

### 2. Auto Trading
`python
from solsniper.auto_trader import AutoTrader, CONSERVATIVE_STRATEGY

trader = AutoTrader(wallet_address="YOUR_WALLET")
trader.add_strategy(CONSERVATIVE_STRATEGY)

# Auto buy with TP/SL
order = await trader.execute_buy(token_address, amount=0.1)
`

### 3. Smart Money Tracking
`python
from solsniper.smart_money import SmartMoneyTracker

tracker = SmartMoneyTracker()
top_wallets = await tracker.get_top_wallets(limit=10)

for wallet in top_wallets:
    print(f"{wallet.address}: {wallet.win_rate}% win rate")
`

## Comparison

| Feature | Trojan | Banana Gun | Photon | Maestro | **SolSniper** |
|---------|--------|------------|--------|---------|---------------|
| Trading Fees | 1% | 0.5% | 1% | 1%+/mo | **0%** |
| AI Rug Detection | No | No | No | Basic | **Real ML** |
| Token Scoring | No | No | No | No | **0.0-1.0** |
| Auto Trading | Yes | Yes | No | Yes | **Yes+TP/SL** |
| Smart Money | Yes | No | No | Yes | **Yes+Score** |
| Self-Hosted | No | No | No | No | **Yes** |
| Open Source | No | No | No | No | **Yes** |

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Self-Hosted** | FREE | Full access, your RPC, your keys |
| **Pro Monthly** | /mo | Hosted RPC, Telegram bot, copy trading |
| **Pro Lifetime** |  | One-time payment, lifetime updates |

## Documentation

- [Landing Page](https://ezequiellich44-cmd.github.io/SolSniper/)
- [Blog: How to Detect Rug Pulls](https://github.com/ezequiellich44-cmd/SolSniper/blob/main/docs/blog/how-to-detect-solana-rug-pulls.md)
- [Blog: Best Solana Trading Bots 2024](https://github.com/ezequiellich44-cmd/SolSniper/blob/main/docs/blog/best-solana-trading-bots-2024.md)
- [FAQ](https://github.com/ezequiellich44-cmd/SolSniper/blob/main/docs/FAQ.md)

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## License

MIT License - see [LICENSE](LICENSE) for details.

---

<p align="center">
  <strong>Built for the Solana community</strong><br>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper">Get Started Free</a> | <a href="https://github.com/ezequiellich44-cmd/SolSniper/issues/1">Buy Pro Lifetime</a>
</p>