"""SolSniper CLI — main entry point."""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

import click

from solsniper import __version__
from solsniper.core.engine import SniperEngine, SniperConfig, Source, TradeAction, TokenInfo
from solsniper.anti_rug.detector import RugDetector
from solsniper.copytrade.engine import CopyTrader, CopyTradeConfig
from solsniper.jito.optimizer import JitoOptimizer
from solsniper.telegram.bot import TelegramBot, TelegramConfig


@click.group()
@click.version_option(__version__, prog_name="solsniper")
def cli():
    """SolSniper — Premium Solana Sniper Bot.

    Self-hosted, no fees, anti-rug ML, copy trading, Jito bundles.
    """
    pass


@cli.command()
@click.option("--rpc-url", default="https://api.mainnet-beta.solana.com", help="Solana RPC URL")
@click.option("--private-key", envvar="SOLANA_PRIVATE_KEY", help="Private key (base58)")
@click.option("--buy-amount", default=0.1, help="Buy amount in SOL")
@click.option("--slippage", default=500, help="Slippage in basis points")
@click.option("--use-jito/--no-jito", default=True, help="Use Jito bundles")
@click.option("--detect-rugs/--no-detect-rugs", default=True, help="Enable rug detection")
@click.option("--copy-trade/--no-copy-trade", default=False, help="Enable copy trading")
@click.option("--copy-wallets", multiple=True, help="Wallets to copy")
@click.option("--telegram-token", envvar="TELEGRAM_BOT_TOKEN", help="Telegram bot token")
@click.option("--telegram-chat", envvar="TELEGRAM_CHAT_ID", help="Telegram chat ID")
def start(
    rpc_url: str,
    private_key: str,
    buy_amount: float,
    slippage: int,
    use_jito: bool,
    detect_rugs: bool,
    copy_trade: bool,
    copy_wallets: tuple,
    telegram_token: str,
    telegram_chat: str,
):
    """Start the sniper engine."""
    config = SniperConfig(
        rpc_url=rpc_url,
        private_key=private_key,
        buy_amount_sol=buy_amount,
        slippage_bps=slippage,
        use_jito=use_jito,
        detect_rugs=detect_rugs,
        copy_trade=copy_trade,
        copy_wallets=list(copy_wallets),
    )

    engine = SniperEngine(config)

    # Setup Telegram
    if telegram_token:
        tg_config = TelegramConfig(
            bot_token=telegram_token,
            chat_id=telegram_chat,
        )
        tg_bot = TelegramBot(tg_config)

        async def on_trade(result):
            await tg_bot.alert_trade(result)

        engine.on_trade(on_trade)

    # Setup copy trading
    if copy_trade and copy_wallets:
        copy_config = CopyTradeConfig()
        copy_trader = CopyTrader(copy_config)
        for wallet in copy_wallets:
            copy_trader.add_wallet(wallet)
        print(f"[SolSniper] Copy trading {len(copy_wallets)} wallets")

    # Token detection callback
    async def on_token(token: TokenInfo) -> TradeAction:
        if detect_rugs:
            detector = RugDetector()
            score = await detector.score(token)
            if score > 0.7:
                print(f"[SolSniper] RUG DETECTED: {token.symbol} (score: {score:.2f})")
                if telegram_token:
                    await tg_bot.alert_rug_detected(token, score)
                return TradeAction.SKIP

        print(f"[SolSniper] NEW TOKEN: {token.name} ({token.symbol}) from {token.source.value}")
        return TradeAction.BUY

    engine.on_new_token(on_token)

    print(f"[SolSniper] Starting with {buy_amount} SOL per snipe")
    print(f"[SolSniper] Jito: {'ON' if use_jito else 'OFF'}")
    print(f"[SolSniper] Rug detection: {'ON' if detect_rugs else 'OFF'}")
    print(f"[SolSniper] Copy trading: {'ON' if copy_trade else 'OFF'}")

    asyncio.run(engine.start())


@cli.command()
@click.option("--rpc-url", default="https://api.mainnet-beta.solana.com")
def scan(rpc_url: str):
    """Scan for new tokens (dry run, no trading)."""
    print("[SolSniper] Scanning for new tokens (dry run)...")
    print("[SolSniper] Press Ctrl+C to stop")

    config = SniperConfig(rpc_url=rpc_url)
    engine = SniperEngine(config)

    async def on_token(token: TokenInfo) -> TradeAction:
        detector = RugDetector()
        score = await detector.score(token)
        status = "RUG" if score > 0.7 else "SAFE"
        print(f"[{status}] {token.name} ({token.symbol}) — {token.source.value} — risk: {score:.2f}")
        return TradeAction.SKIP

    engine.on_new_token(on_token)
    asyncio.run(engine.start())


@cli.command()
def serve():
    """Start the API server (hosted version)."""
    import uvicorn
    from solsniper.api.server import app

    print("[SolSniper] Starting API server on port 8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)


@cli.command()
def status():
    """Show current status and configuration."""
    print(f"SolSniper v{__version__}")
    print("=" * 40)
    print(f"RPC: not configured")
    print(f"Jito: available")
    print(f"Anti-rug: available")
    print(f"Copy trading: available")
    print(f"Telegram: not configured")
    print("=" * 40)
    print("Run 'solsniper start' to begin sniping")


def main():
    cli()


if __name__ == "__main__":
    main()
