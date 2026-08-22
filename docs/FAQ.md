# SolSniper FAQ

## General

### What is SolSniper?
SolSniper is an open-source Solana trading bot with built-in anti-rug machine learning. It analyzes tokens in real-time to detect rug pulls before you trade.

### Is SolSniper free?
Yes! SolSniper is free for self-hosted use. Pro plans start at $49/month for hosted infrastructure.

### How does anti-rug detection work?
SolSniper queries DexScreener API and Solana RPC to check:
- Mint authority status
- Freeze authority status
- Holder distribution
- Liquidity depth
- Honeypot patterns

### What is token scoring?
Every token analyzed gets a risk score from 0.0 to 1.0. Lower scores mean safer tokens.

## Technical

### What Python version is required?
Python 3.9 or higher.

### How do I install SolSniper?
```bash
pip install git+https://github.com/ezequiellich44-cmd/SolSniper.git
```

### How do I scan a token?
```bash
solsniper scan <TOKEN_ADDRESS>
```

### How do I start the bot?
```bash
solsniper start
```

### What RPC does SolSniper use?
You can use any Solana RPC. For best results, use a private RPC with Jito support.

## Pricing

### What is included in the free plan?
- Anti-rug ML engine
- Token scoring
- CLI + Python SDK
- Community support

### What is included in Pro?
- Everything in Free
- Hosted RPC + Jito
- Telegram bot alerts
- Copy trading scoring
- 1000 tx/mo
- Auto-updates

### How do I upgrade?
Open an issue on GitHub: https://github.com/ezequiellich44-cmd/SolSniper/issues/1

## Support

### Where can I get help?
- GitHub Issues: https://github.com/ezequiellich44-cmd/SolSniper/issues
- Documentation: https://github.com/ezequiellich44-cmd/SolSniper/tree/main/docs

### How do I report a bug?
Open an issue with steps to reproduce.

### How do I request a feature?
Open an issue with the feature description.
