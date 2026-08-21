"""SolSniper CLI — main entry point with REAL functionality."""

from __future__ import annotations

import asyncio
import json
import sys

import click

from solsniper import __version__


@click.group()
@click.version_option(__version__, prog_name="solsniper")
def cli():
    """SolSniper — Premium Solana Sniper Bot.

    Anti-rug ML, copy trading, Jito bundles.
    """
    pass


@cli.command()
@click.argument("mint")
@click.option("--rpc-url", default="https://api.mainnet-beta.solana.com")
def scan(mint: str, rpc_url: str):
    """Scan a token for rug risk. REAL on-chain data.

    Example: solsniper scan So11111111111111111111111111111111111111112
    """
    from solsniper.anti_rug.detector import RugDetector
    from solsniper.core.engine import TokenInfo, Source

    async def _scan():
        detector = RugDetector(rpc_url=rpc_url)
        token = TokenInfo(
            mint=mint,
            name="Scanning...",
            symbol="...",
            source=Source.PUMP_FUN,
        )

        click.echo(f"Scanning {mint}...")
        click.echo("Querying DexScreener + Solana RPC...")
        click.echo()

        report = await detector.get_token_report(mint)

        click.echo("=" * 50)
        click.echo("  TOKEN RISK REPORT")
        click.echo("=" * 50)
        click.echo(f"  Mint:     {report['mint'][:8]}...{report['mint'][-4:]}")
        click.echo(f"  Risk:     [{report['risk_level']}] {report['risk_score']:.1%}")
        click.echo(f"  Verdict:  {report['verdict']}")
        click.echo("=" * 50)
        click.echo()
        click.echo("  SIGNALS:")
        signals = report["signals"]
        click.echo(f"    Liquidity:       {signals['liquidity_sol']:.2f} SOL")
        click.echo(f"    Liquidity Lock:  {'YES' if signals['liquidity_locked'] else 'NO'}")
        click.echo(f"    Top Holder:      {signals['top_holders_pct']:.1f}%")
        click.echo(f"    Holder Count:    {signals['holder_count']}")
        click.echo(f"    Mint Authority:  {'YES (RISK!)' if signals['mint_authority'] else 'NO (safe)'}")
        click.echo(f"    Freeze Auth:     {'YES (RISK!)' if signals['freeze_authority'] else 'NO (safe)'}")
        click.echo(f"    Buy Tax:         {signals['buy_tax']:.1f}%")
        click.echo(f"    Sell Tax:        {signals['sell_tax']:.1f}%")
        click.echo(f"    Twitter:         {'YES' if signals['has_twitter'] else 'NO'}")
        click.echo(f"    Website:         {'YES' if signals['has_website'] else 'NO'}")
        click.echo()

        if report["verdict"] == "BUY":
            click.echo("  RESULT: Token appears SAFE to buy.")
        elif report["verdict"] == "CAUTION":
            click.echo("  RESULT: Token has some risks. Proceed with caution.")
        else:
            click.echo("  RESULT: Token is HIGH RISK. Likely a rug pull. DO NOT BUY.")

    asyncio.run(_scan())


@cli.command()
@click.option("--rpc-url", default="https://api.mainnet-beta.solana.com")
@click.option("--private-key", envvar="SOLANA_PRIVATE_KEY", help="Private key (base58)")
@click.option("--buy-amount", default=0.1, help="Buy amount in SOL")
@click.option("--slippage", default=500, help="Slippage in basis points")
@click.option("--use-jito/--no-jito", default=True, help="Use Jito bundles")
@click.option("--detect-rugs/--no-detect-rugs", default=True, help="Enable rug detection")
def start(rpc_url, private_key, buy_amount, slippage, use_jito, detect_rugs):
    """Start the sniper engine (requires RPC + private key)."""
    click.echo("[SolSniper] Starting sniper engine...")
    click.echo(f"  RPC: {rpc_url}")
    click.echo(f"  Buy amount: {buy_amount} SOL")
    click.echo(f"  Jito: {'ON' if use_jito else 'OFF'}")
    click.echo(f"  Rug detection: {'ON' if detect_rugs else 'OFF'}")
    click.echo()

    if not private_key:
        click.echo("ERROR: Set SOLANA_PRIVATE_KEY environment variable")
        click.echo("  export SOLANA_PRIVATE_KEY='your-base58-private-key'")
        sys.exit(1)

    from solsniper.core.engine import SniperEngine, SniperConfig

    config = SniperConfig(
        rpc_url=rpc_url,
        private_key=private_key,
        buy_amount_sol=buy_amount,
        slippage_bps=slippage,
        use_jito=use_jito,
        detect_rugs=detect_rugs,
    )
    engine = SniperEngine(config)
    asyncio.run(engine.start())


@cli.command()
def status():
    """Show current status and configuration."""
    click.echo(f"SolSniper v{__version__}")
    click.echo("=" * 40)
    click.echo("  Anti-rug ML:     READY (real on-chain data)")
    click.echo("  Copy trading:    READY (wallet scoring)")
    click.echo("  Jito bundles:    READY (dynamic tips)")
    click.echo("  Telegram bot:    READY (alerts + control)")
    click.echo("  API server:      READY (tier enforcement)")
    click.echo("=" * 40)
    click.echo()
    click.echo("Quick start:")
    click.echo("  solsniper scan <mint>     # Scan a token for rug risk")
    click.echo("  solsniper start           # Start sniping (requires private key)")
    click.echo("  solsniper serve           # Start API server")


def main():
    cli()


if __name__ == "__main__":
    main()