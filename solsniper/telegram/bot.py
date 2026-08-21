"""Telegram bot — remote control and alerts for SolSniper."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import Optional

from solsniper.core.engine import TradeResult, TokenInfo


@dataclass
class TelegramConfig:
    """Telegram bot configuration."""

    bot_token: str = ""
    chat_id: str = ""
    alert_on_snipe: bool = True
    alert_on_rug: bool = True
    alert_on_copy: bool = True
    alert_on_pnl: bool = True
    min_pnl_alert_pct: float = 10.0


class TelegramBot:
    """Telegram bot for SolSniper alerts and control.

    Features:
    - Real-time snipe alerts with token info
    - Rug detection alerts
    - Copy trade notifications
    - P&L reports on demand
    - Remote control (buy/sell commands)
    """

    def __init__(self, config: TelegramConfig):
        self.config = config
        self._running = False
        self._message_queue: list[dict] = []

    async def start(self) -> None:
        """Start the Telegram bot."""
        if not self.config.bot_token:
            print("[SolSniper] Telegram bot: no token configured, alerts disabled")
            return

        self._running = True
        print("[SolSniper] Telegram bot started")

        # In production: use python-telegram-bot or aiogram
        # For now: queue messages for later sending
        while self._running:
            await asyncio.sleep(1)
            await self._process_queue()

    async def stop(self) -> None:
        """Stop the Telegram bot."""
        self._running = False

    async def _process_queue(self) -> None:
        """Process queued messages."""
        while self._message_queue:
            msg = self._message_queue.pop(0)
            await self._send_message(msg["text"], msg.get("parse_mode"))

    async def _send_message(self, text: str, parse_mode: str = "HTML") -> None:
        """Send a message to the configured chat via Telegram Bot API."""
        if not self.config.bot_token or not self.config.chat_id:
            return

        import httpx

        try:
            async with httpx.AsyncClient() as client:
                url = f"https://api.telegram.org/bot{self.config.bot_token}/sendMessage"
                resp = await client.post(
                    url,
                    json={
                        "chat_id": self.config.chat_id,
                        "text": text,
                        "parse_mode": parse_mode,
                    },
                    timeout=10.0,
                )
                if resp.status_code != 200:
                    print(f"[Telegram] Error sending message: {resp.status_code}")
        except Exception as e:
            print(f"[Telegram] Error: {e}")

    async def send_command(self, command: str) -> dict:
        """Handle a Telegram command."""
        commands = {
            "/start": self._cmd_start,
            "/stop": self._cmd_stop,
            "/status": self._cmd_status,
            "/scan": self._cmd_scan,
            "/positions": self._cmd_positions,
        }

        handler = commands.get(command)
        if handler:
            return await handler()
        return {"error": f"Unknown command: {command}"}

    async def _cmd_start(self) -> dict:
        """Start sniping."""
        return {"action": "start", "message": "Sniping started"}

    async def _cmd_stop(self) -> dict:
        """Stop sniping."""
        return {"action": "stop", "message": "Sniping stopped"}

    async def _cmd_status(self) -> dict:
        """Get status."""
        return {"action": "status", "stats": self.get_stats()}

    async def _cmd_scan(self) -> dict:
        """Scan a token."""
        return {"action": "scan", "message": "Use /scan <mint>"}

    async def _cmd_positions(self) -> dict:
        """Get positions."""
        return {"action": "positions", "message": "No open positions"}

    async def alert_new_token(self, token: TokenInfo, action: str) -> None:
        """Alert about a new detected token."""
        if not self.config.alert_on_snipe:
            return

        text = (
            f"🎯 <b>New Token Detected</b>\n\n"
            f"<b>Name:</b> {token.name} ({token.symbol})\n"
            f"<b>Source:</b> {token.source.value}\n"
            f"<b>Mint:</b> <code>{token.mint[:8]}...{token.mint[-4:]}</code>\n"
            f"<b>Liquidity:</b> {token.initial_liquidity:.2f} SOL\n"
            f"<b>Action:</b> {action}\n"
        )
        self._message_queue.append({"text": text})

    async def alert_trade(self, result: TradeResult) -> None:
        """Alert about a trade execution."""
        emoji = "✅" if result.success else "❌"
        status = "SUCCESS" if result.success else "FAILED"

        text = (
            f"{emoji} <b>Trade {status}</b>\n\n"
            f"<b>Action:</b> {result.action.value.upper()}\n"
            f"<b>Amount:</b> {result.amount_sol:.4f} SOL\n"
            f"<b>Token:</b> {result.token.symbol if result.token else 'N/A'}\n"
            f"<b>TX:</b> <code>{result.tx_hash or 'N/A'}</code>\n"
        )

        if result.error:
            text += f"<b>Error:</b> {result.error}\n"

        self._message_queue.append({"text": text})

    async def alert_rug_detected(self, token: TokenInfo, score: float) -> None:
        """Alert about a detected rug pull."""
        if not self.config.alert_on_rug:
            return

        text = (
            f"🚨 <b>RUG DETECTED</b>\n\n"
            f"<b>Token:</b> {token.name} ({token.symbol})\n"
            f"<b>Risk Score:</b> {score:.0%}\n"
            f"<b>Mint:</b> <code>{token.mint[:8]}...{token.mint[-4:]}</code>\n"
            f"<b>Action:</b> SKIPPED\n"
        )
        self._message_queue.append({"text": text})

    async def alert_copy_trade(self, wallet: str, token: TokenInfo) -> None:
        """Alert about a copy trade execution."""
        if not self.config.alert_on_copy:
            return

        text = (
            f"📋 <b>Copy Trade</b>\n\n"
            f"<b>Following:</b> <code>{wallet[:8]}...{wallet[-4:]}</code>\n"
            f"<b>Token:</b> {token.name} ({token.symbol})\n"
            f"<b>Mint:</b> <code>{token.mint[:8]}...{token.mint[-4:]}</code>\n"
        )
        self._message_queue.append({"text": text})

    async def send_pnl_report(self, positions: dict, total_pnl: float) -> None:
        """Send a P&L report."""
        emoji = "📈" if total_pnl >= 0 else "📉"

        text = f"{emoji} <b>P&L Report</b>\n\n"

        if not positions:
            text += "No open positions.\n"
        else:
            for mint, pos in positions.items():
                text += f"• <code>{mint[:8]}...{mint[-4:]}</code>: {pos.get('pnl_pct', 0):+.1f}%\n"

        text += f"\n<b>Total P&L:</b> {total_pnl:+.2f} SOL"
        self._message_queue.append({"text": text})

    def get_stats(self) -> dict:
        """Get Telegram bot statistics."""
        return {
            "running": self._running,
            "queued_messages": len(self._message_queue),
            "config": {
                "alert_on_snipe": self.config.alert_on_snipe,
                "alert_on_rug": self.config.alert_on_rug,
                "alert_on_copy": self.config.alert_on_copy,
            },
        }
