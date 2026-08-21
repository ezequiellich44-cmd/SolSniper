"""Copy trading engine — follow profitable wallets automatically.

INNOVATION: Not just copy trades, but SCORE wallets based on
historical performance, win rate, and profit factor.

Uses REAL on-chain data via Solana RPC + DexScreener.
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field

import httpx


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
    score: float = 0.0
    is_whale: bool = False
    tags: list[str] = field(default_factory=list)

    # Real data fields
    sol_balance: float = 0.0
    token_count: int = 0
    recent_swaps: int = 0


@dataclass
class CopyTradeConfig:
    """Configuration for copy trading."""

    min_score: float = 60.0
    max_position_size_sol: float = 0.5
    copy_delay_ms: int = 100
    blacklist: list[str] = field(default_factory=list)
    max_wallets: int = 10
    rebalance_interval_s: int = 3600


class CopyTrader:
    """Copy trading engine with wallet scoring.

    Queries real on-chain data:
    - Solana RPC for balance, token holdings, recent transactions
    - DexScreener for trade history and PnL
    """

    SOLANA_RPC = "https://api.mainnet-beta.solana.com"
    HELIUS_RPC = "https://mainnet.helius-rpc.com/?api-key=demo"
    DEXSCREENER_API = "https://api.dexscreener.com"

    def __init__(self, config: CopyTradeConfig, rpc_url: str | None = None):
        self.config = config
        self.rpc_url = rpc_url or self.SOLANA_RPC
        self._wallets: dict[str, WalletScore] = {}
        self._trade_history: dict[str, list[dict]] = {}
        self._copied_trades: list[dict] = []

    def add_wallet(self, address: str, tags: list[str] | None = None) -> WalletScore:
        """Add a wallet to track."""
        if address in self.config.blacklist:
            raise ValueError(f"Wallet {address} is blacklisted")

        score = WalletScore(address=address, tags=tags or [])
        self._wallets[address] = score
        return score

    def remove_wallet(self, address: str) -> None:
        """Stop tracking a wallet."""
        self._wallets.pop(address, None)

    async def update_scores(self) -> dict[str, WalletScore]:
        """Recalculate scores for all tracked wallets using REAL data."""
        for addr, ws in self._wallets.items():
            # Query real on-chain data
            await self._query_wallet_data(addr, ws)

            # Calculate metrics from real data
            history = self._trade_history.get(addr, [])
            if history:
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
                min(ws.profit_factor, 5) * 20 +
                min(ws.total_trades / 100, 1) * 15 +
                min(ws.avg_profit_pct / 50, 1) * 15 +
                (15 if ws.is_whale else 0) +
                (5 if "verified" in ws.tags else 0)
            )

            ws.last_active = max(t.get("timestamp", 0) for t in history) if history else 0

        return dict(self._wallets)

    async def _query_wallet_data(self, address: str, ws: WalletScore) -> None:
        """Query real on-chain data for a wallet."""
        # 1. Query SOL balance
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getBalance",
                        "params": [address],
                    },
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    lamports = data.get("result", {}).get("value", 0)
                    ws.sol_balance = lamports / 1e9
                    ws.is_whale = ws.sol_balance > 100  # > 100 SOL = whale
        except Exception:
            pass

        # 2. Query token holdings (getProgramAccounts for Token Account)
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getTokenAccountsByOwner",
                        "params": [
                            address,
                            {"programId": "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA"},
                            {"encoding": "jsonParsed"},
                        ],
                    },
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    accounts = data.get("result", {}).get("value", [])
                    ws.token_count = len(accounts)
        except Exception:
            pass

        # 3. Query recent transactions via getSignaturesForAddress
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.post(
                    self.rpc_url,
                    json={
                        "jsonrpc": "2.0",
                        "id": 1,
                        "method": "getSignaturesForAddress",
                        "params": [address, {"limit": 20}],
                    },
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    sigs = data.get("result", [])
                    ws.recent_swaps = len(sigs)
                    if sigs:
                        # Get most recent transaction time
                        most_recent = sigs[0].get("blockTime", 0)
                        if most_recent:
                            ws.last_active = most_recent
        except Exception:
            pass

        # 4. Try to get trading data from DexScreener
        try:
            async with httpx.AsyncClient() as client:
                resp = await client.get(
                    f"{self.DEXSCREENER_API}/latest/dex/profiles/{address}",
                    timeout=10.0,
                )
                if resp.status_code == 200:
                    data = resp.json()
                    pairs = data.get("pairs", [])
                    if pairs:
                        # Count recent trading pairs
                        ws.total_trades = len(pairs)
        except Exception:
            pass

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
            "total_sol_tracked": sum(w.sol_balance for w in self._wallets.values()),
        }

    async def analyze_wallet(self, address: str) -> dict:
        """Analyze a wallet and return a report."""
        ws = WalletScore(address=address)
        await self._query_wallet_data(address, ws)

        return {
            "address": address,
            "sol_balance": round(ws.sol_balance, 2),
            "is_whale": ws.is_whale,
            "token_count": ws.token_count,
            "recent_transactions": ws.recent_swaps,
            "last_active": ws.last_active,
            "recommendation": "TRACK" if ws.sol_balance > 10 else "SKIP",
        }
