# SolSniper - Anti-Rug ML Bot for Solana

<p align="center">
  <strong>Detect Rug Pulls Before You Buy</strong><br>
  Real on-chain data. Real protection. Real results.
</p>

<p align="center">
  <a href="https://github.com/ezequiellich44-cmd/SolSniper/actions"><img src="https://github.com/ezequiellich44-cmd/SolSniper/actions/workflows/test.yml/badge.svg" alt="Tests"></a>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper/blob/main/LICENSE"><img src="https://img.shields.io/badge/license-MIT-green.svg" alt="License"></a>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper"><img src="https://img.shields.io/badge/python-3.9+-blue.svg" alt="Python"></a>
</p>

---

## Why SolSniper?

**Every day, traders lose millions to rug pulls on Solana.** Existing bots like Trojan, Banana Gun, and Photon charge 0.5-1% per trade but offer ZERO anti-rug protection.

**SolSniper is different.** It's the ONLY tool with real anti-rug machine learning that queries DexScreener + Solana RPC to detect rug pulls before you trade.

## Features

| Feature | Description | Benefit |
|---------|-------------|---------|
| **Anti-Rug ML** | Queries DexScreener + Solana RPC in real-time | Detect mint/freeze authority, honeypots |
| **Token Scoring 0.0-1.0** | Every token gets a risk score | Make informed decisions in milliseconds |
| **Jito Bundles** | Private mempool execution | No front-running, no sandwich attacks |
| **0% Trading Fees** | Keep 100% of your profits | vs 0.5-1% on Trojan/Banana Gun |
| **Copy Trading** | Copy top wallets with scoring | See win rate before copying |
| **Telegram Bot** | Real-time alerts | Trade from your phone |
| **Self-Hosted** | Your keys, your control | No trust required |
| **Open Source** | Full transparency | Audit the code yourself |

## Quick Start

```bash
# Install
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git

# Scan a token
solsniper scan <TOKEN_ADDRESS>

# Start bot
solsniper start
```

## Anti-Rug Detection

SolSniper analyzes:

- **Mint Authority**: Can dev mint more tokens? (HUGE red flag)
- **Freeze Authority**: Can dev freeze your wallet?
- **Holder Distribution**: Is one wallet holding too much?
- **Liquidity**: Is there enough liquidity to trade?
- **Social Signals**: Does the token have real community?

## Token Scoring

Every token gets a score from 0.0 to 1.0:

| Score | Risk Level | Action |
|-------|------------|--------|
| 0.0-0.2 | LOW | Safe to trade |
| 0.2-0.4 | MEDIUM | Trade with caution |
| 0.4-0.6 | HIGH | Likely rug pull |
| 0.6-0.8 | VERY HIGH | Do NOT trade |
| 0.8-1.0 | EXTREME | Definite rug pull |

## Comparison

| Feature | Trojan | Banana Gun | Photon | **SolSniper** |
|---------|--------|------------|--------|---------------|
| Trading Fees | 1% | 0.5-1% | ~0.5% | **0%** |
| Anti-Rug Protection | No | No | No | **Yes (ML)** |
| Token Scoring | No | No | No | **0.0-1.0** |
| Self-Hosted | No | No | No | **Yes** |
| Jito Bundles | Yes | Yes | Yes | **Yes** |
| Copy Trading | Yes | No | No | **Yes + Scoring** |
| Open Source | No | No | No | **Yes** |

## Pricing

| Plan | Price | Features |
|------|-------|----------|
| **Self-Hosted** | FREE | Full anti-rug ML, CLI, Python SDK |
| **Pro Monthly** | $49/mo | Hosted RPC, Telegram bot, copy trading |
| **Pro Lifetime** | $249 | One-time payment, lifetime updates |

## Installation

```bash
# From source
git clone https://github.com/ezequiellich44-cmd/SolSniper.git
cd SolSniper
pip install -e .

# Or directly
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git
```

## CLI Commands

```bash
# Scan a token for rug pull risk
solsniper scan <TOKEN_ADDRESS>

# View wallet balance
solsniper wallet <WALLET_ADDRESS>

# Start the bot
solsniper start

# Run demo
solsniper demo

# Check status
solsniper status
```

## License

MIT License - see [LICENSE](LICENSE) for details.

## Contributing

Contributions welcome! Please read our [Contributing Guide](CONTRIBUTING.md) first.

## Support

- [GitHub Issues](https://github.com/ezequiellich44-cmd/SolSniper/issues)
- [Documentation](https://github.com/ezequiellich44-cmd/SolSniper/tree/main/docs)

---

<p align="center">
  <strong>Built for the Solana community</strong><br>
  <a href="https://github.com/ezequiellich44-cmd/SolSniper">Get Started Free</a>
</p>
