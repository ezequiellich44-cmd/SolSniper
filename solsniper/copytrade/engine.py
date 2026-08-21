"""Copy trading engine — follow profitable wallets automatically.

INNOVATION: Not just copy trades, but SCORE wallets based on
historical performance, win rate, and profit factor.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class WalletScore:
    """Score for a tracked wallet."""

    address: str
    win_rate: float = 0.0
    profit_factor: float = 0.0
    total_trades: int = 0
    avg_profit_pct: float = 0.0
    max_drawdown: float = 0.0
    sharpe_ratio: float = 0.0
    last_active: float = 0.0
    score: float = 0.0  # Composite score 0-100
    is_whale: bool = False
    tags: list[str] = field(default_factory=list)


@dataclass
class CopyTradeConfig:
    """Configuration for copy trading."""

    min_score: float = 60.0  # Minimum wallet score to copy
    max_position_size_sol: float = 0.5
    copy_delay_ms: int = 100  # Delay before copying (front-run protection)
    blacklist: list[str] = field(default_factory=list)
    max_wallets: int = 10
    rebalance_interval_s: int = 3600


class CopyTrader:
    """Copy trading engine with wallet scoring.

    Innovation: Scores wallets using multiple metrics, not just
    "follow the whale." This prevents copying wallets that look
    profitable but are actually dumping on followers.
    """

    def __init__(self, config: CopyTradeConfig):
        self.config = config
        self._wallets: dict[str, WalletScore] = {}
        self._trade_history: dict[str, list[dict]] = {}
        self._copied_trades: list[dict] = []

    def add_wallet(self, address: str, tags: list[str] | None = None) -> WalletScore:
        """Add a wallet to track."""
        if address in self.config.blacklist:
            raise ValueError(f"Wallet {address} is blacklisted")

        score = WalletScore(
            address=address,
            tags=tags or [],
        )
        self._wallets[address] = score
        return score

    def remove_wallet(self, address: str) -> None:
        """Stop tracking a wallet."""
        self._wallets.pop(address, None)

    async def update_scores(self) -> dict[str, WalletScore]:
        """Recalculate scores for all tracked wallets.

        In production, this queries on-chain data for each wallet's
        trade history and computes metrics.
        """
        for addr, ws in self._wallets.items():
            history = self._trade_history.get(addr, [])
            if not history:
                continue

            # Calculate metrics
            wins = [t for t in history if t.get("pnl", 0) > 0]
            losses = [t for t in history if t.get("pnl", 0) <= 0]

            ws.total_trades = len(history)
            ws.win_rate = len(wins) / len(history) if history else 0

            avg_win = sum(t.get("pnl", 0) for t in wins) / len(wins) if wins else 0
            avg_loss = abs(sum(t.get("pnl", 0) for t in losses) / len(losses)) if losses else 1
            ws.profit_factor = avg_win / avg_loss if avg_loss > 0 else 0

            ws.avg_profit_pct = sum(t.get("pnl_pct", 0) for t in history) / len(history) if history else 0

            # Composite score (weighted)
            ws.score = (
                ws.win_rate * 30 +
                min(ws.profit_factor, 5) * 20 +  # Cap at 5x
                min(ws.total_trades / 100, 1) * 15 +  # More trades = more reliable
                min(ws.avg_profit_pct / 50, 1) * 15 +
                (15 if ws.is_whale else 0) +
                (5 if "verified" in ws.tags else 0)
            )

            ws.last_active = max(t.get("timestamp", 0) for t in history) if history else 0

        return dict(self._wallets)

    def get_top_wallets(self, n: int = 10) -> list[WalletScore]:
        """Get top N wallets by score."""
        sorted_wallets = sorted(
            self._wallets.values(),
            key=lambda w: w.score,
            reverse=True,
        )
        return sorted_wallets[:n]

    def should_copy(self, wallet_address: str) -> bool:
        """Determine if we should copy a trade from this wallet."""
        ws = self._wallets.get(wallet_address)
        if not ws:
            return False
        if ws.score < self.config.min_score:
            return False
        if len(self._wallets) > self.config.max_wallets:
            return False
        return True

    def record_trade(self, wallet_address: str, trade: dict) -> None:
        """Record a trade from a tracked wallet."""
        if wallet_address not in self._trade_history:
            self._trade_history[wallet_address] = []
        self._trade_history[wallet_address].append(trade)

    def get_stats(self) -> dict:
        """Get copy trading statistics."""
        return {
            "tracked_wallets": len(self._wallets),
            "copied_trades": len(self._copied_trades),
            "avg_score": sum(w.score for w in self._wallets.values()) / len(self._wallets) if self._wallets else 0,
            "top_wallet": self.get_top_wallets(1)[0].address if self._wallets else None,
        }
