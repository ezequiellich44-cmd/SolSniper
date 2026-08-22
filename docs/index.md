# SolSniper Documentation

## What is SolSniper?

SolSniper is an open-source Solana trading bot with built-in anti-rug machine learning. It analyzes tokens in real-time using DexScreener API and Solana RPC to detect rug pulls before you trade.

## Key Features

### Anti-Rug Machine Learning
SolSniper queries multiple on-chain data sources to detect:
- Mint authority (can dev create more tokens?)
- Freeze authority (can dev freeze your wallet?)
- Holder concentration (is one wallet holding too much?)
- Liquidity depth (can you sell when you want?)
- Honeypot patterns (can you buy but not sell?)

### Token Scoring System
Every token analyzed gets a risk score from 0.0 to 1.0:
- 0.0-0.2: Low risk (safe to trade)
- 0.2-0.4: Medium risk (trade with caution)
- 0.4-0.6: High risk (likely rug pull)
- 0.6-0.8: Very high risk (do not trade)
- 0.8-1.0: Extreme risk (definite rug pull)

### Jito Bundle Integration
SolSniper uses Jito bundles for private mempool execution. Your trades never hit the public mempool, preventing:
- Front-running
- Sandwich attacks
- MEV extraction

### Copy Trading
Copy top-performing wallets with built-in risk scoring:
- Win rate analysis
- Profit factor calculation
- Risk level assessment
- Trade history review

### Zero Trading Fees
Unlike Trojan (1%), Banana Gun (0.5-1%), and Photon (~0.5%), SolSniper charges zero trading fees. Keep 100% of your profits.

## Installation

```bash
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git
```

## Usage

```bash
# Scan a token
solsniper scan <TOKEN_ADDRESS>

# Start the bot
solsniper start

# Run demo
solsniper demo
```

## Comparison with Other Bots

| Feature | Trojan | Banana Gun | Photon | SolSniper |
|---------|--------|------------|--------|-----------|
| Trading Fees | 1% | 0.5-1% | ~0.5% | 0% |
| Anti-Rug Protection | No | No | No | Yes |
| Token Scoring | No | No | No | 0.0-1.0 |
| Self-Hosted | No | No | No | Yes |
| Open Source | No | No | No | Yes |

## Pricing

- **Self-Hosted**: Free forever
- **Pro Monthly**: $49/month
- **Pro Lifetime**: $249 one-time

## Links

- [GitHub Repository](https://github.com/ezequiellich44-cmd/SolSniper)
- [Landing Page](https://ezequiellich44-cmd.github.io/SolSniper/)
- [Issues](https://github.com/ezequiellich44-cmd/SolSniper/issues)
