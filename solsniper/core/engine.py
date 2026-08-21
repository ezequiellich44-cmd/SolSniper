"""Core sniper engine — monitors pump.fun and Raydium for new pools."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Optional, Callable, Awaitable

from solders.keypair import Keypair  # type: ignore
from solders.transaction import VersionedTransaction  # type: ignore


class Source(str, Enum):
    PUMP_FUN = "pump.fun"
    RAYDIUM = "raydium"


class TradeAction(str, Enum):
    BUY = "buy"
    SELL = "sell"
    SKIP = "skip"


@dataclass
class TokenInfo:
    """Metadata about a newly detected token."""

    mint: str
    name: str
    symbol: str
    source: Source
    pool_address: str | None = None
    initial_liquidity: float = 0.0
    dev_wallet: str | None = None
    timestamp: float = field(default_factory=time.time)
    metadata_uri: str | None = None


@dataclass
class SniperConfig:
    """Configuration for the sniper engine."""

    rpc_url: str = "https://api.mainnet-beta.solana.com"
    ws_url: str = "wss://api.mainnet-beta.solana.com"
    private_key: str = ""
    buy_amount_sol: float = 0.1
    slippage_bps: int = 500  # 5%
    priority_fee_lamports: int = 100_000  # 0.0001 SOL
    use_jito: bool = True
    jito_tip_lamports: int = 50_000
    max_concurrent_snipes: int = 5
    min_liquidity_sol: float = 1.0
    max_buy_tax: float = 10.0
    max_sell_tax: float = 10.0
    auto_sell: bool = True
    take_profit_pct: float = 100.0  # 2x
    stop_loss_pct: float = 50.0
    detect_rugs: bool = True
    honeypot_check: bool = True
    copy_trade: bool = False
    copy_wallets: list[str] = field(default_factory=list)


@dataclass
class TradeResult:
    """Result of a sniper trade execution."""

    success: bool
    tx_hash: str | None = None
    token: TokenInfo | None = None
    action: TradeAction = TradeAction.BUY
    amount_sol: float = 0.0
    amount_tokens: float = 0.0
    price: float = 0.0
    slippage: float = 0.0
    error: str | None = None
    timestamp: float = field(default_factory=time.time)


# Type alias for callbacks
OnTokenCallback = Callable[[TokenInfo], Awaitable[TradeAction]]
OnTradeCallback = Callable[[TradeResult], Awaitable[None]]


class SniperEngine:
    """Core engine that monitors DEXes and executes trades.

    Usage:
        config = SniperConfig(private_key="...", buy_amount_sol=0.1)
        engine = SniperEngine(config)

        async def on_token(token: TokenInfo) -> TradeAction:
            return TradeAction.BUY if token.source == Source.PUMP_FUN else TradeAction.SKIP

        engine.on_new_token(on_token)
        await engine.start()
    """

    def __init__(self, config: SniperConfig):
        self.config = config
        self._running = False
        self._active_snipes = 0
        self._tokens_seen: dict[str, float] = {}
        self._on_token_callbacks: list[OnTokenCallback] = []
        self._on_trade_callbacks: list[OnTradeCallback] = []
        self._wallet = Keypair.from_base58_string(config.private_key) if config.private_key else None
        self._positions: dict[str, dict] = {}  # mint -> {entry_price, amount, timestamp}

    def on_new_token(self, callback: OnTokenCallback) -> None:
        """Register callback for new token detection."""
        self._on_token_callbacks.append(callback)

    def on_trade(self, callback: OnTradeCallback) -> None:
        """Register callback for trade execution."""
        self._on_trade_callbacks.append(callback)

    async def start(self) -> None:
        """Start the sniper engine. Listens for new pools."""
        self._running = True
        print("[SolSniper] Engine started — monitoring pump.fun + Raydium")

        # Run pump.fun and Raydium listeners concurrently
        await asyncio.gather(
            self._listen_pumpfun(),
            self._listen_raydium(),
            self._monitor_positions(),
        )

    async def stop(self) -> None:
        """Stop the sniper engine."""
        self._running = False
        print("[SolSniper] Engine stopped")

    async def _listen_pumpfun(self) -> None:
        """Listen for new tokens on pump.fun bonding curve."""
        print("[SolSniper] Listening to pump.fun...")
        # In production: connect to pump.fun WebSocket or geyser plugin
        # For now: simulated detection loop
        while self._running:
            await asyncio.sleep(1)  # Simulate WebSocket polling
            # Real implementation would parse pump.fun program logs
            # and detect when tokens graduate to Raydium

    async def _listen_raydium(self) -> None:
        """Listen for new pools on Raydium AMM."""
        print("[SolSniper] Listening to Raydium...")
        while self._running:
            await asyncio.sleep(1)
            # Real implementation: subscribe to Raydium program logs
            # via Geyser gRPC or WebSocket

    async def _monitor_positions(self) -> None:
        """Monitor open positions for auto-sell (take profit / stop loss)."""
        while self._running:
            await asyncio.sleep(2)
            # Check each position against TP/SL levels
            for mint, pos in list(self._positions.items()):
                # Real implementation: query Jupiter for current price
                pass

    async def snipe(self, token: TokenInfo) -> TradeResult:
        """Execute a snipe trade for a detected token.

        This is the core method that:
        1. Validates the token (anti-rug check)
        2. Builds the swap transaction
        3. Submits via Jito bundle (private, no mempool)
        4. Returns the result
        """
        if self._active_snipes >= self.config.max_concurrent_snipes:
            return TradeResult(
                success=False,
                token=token,
                error="Max concurrent snipes reached",
            )

        if not self._wallet:
            return TradeResult(
                success=False,
                token=token,
                error="No wallet configured",
            )

        self._active_snipes += 1
        try:
            # 1. Anti-rug check (if enabled)
            if self.config.detect_rugs:
                rug_score = await self._check_rug(token)
                if rug_score > 0.8:
                    return TradeResult(
                        success=False,
                        token=token,
                        error=f"Rug detected (score: {rug_score:.2f})",
                    )

            # 2. Honeypot check
            if self.config.honeypot_check:
                is_honeypot = await self._check_honeypot(token)
                if is_honeypot:
                    return TradeResult(
                        success=False,
                        token=token,
                        error="Honeypot detected",
                    )

            # 3. Build swap transaction
            # Real implementation: use Jupiter API or Raydium SDK
            # For now: simulated execution
            tx_hash = f"sim_{token.mint[:8]}_{int(time.time())}"

            result = TradeResult(
                success=True,
                tx_hash=tx_hash,
                token=token,
                action=TradeAction.BUY,
                amount_sol=self.config.buy_amount_sol,
                price=token.initial_liquidity,
            )

            # 4. Track position
            self._positions[token.mint] = {
                "entry_price": token.initial_liquidity,
                "amount": self.config.buy_amount_sol,
                "timestamp": time.time(),
            }

            # 5. Notify callbacks
            for cb in self._on_trade_callbacks:
                await cb(result)

            return result

        except Exception as e:
            return TradeResult(
                success=False,
                token=token,
                error=str(e),
            )
        finally:
            self._active_snipes -= 1

    async def sell(self, mint: str, pct: float = 100.0) -> TradeResult:
        """Sell a position."""
        pos = self._positions.get(mint)
        if not pos:
            return TradeResult(success=False, error=f"No position for {mint}")

        # Real implementation: build sell tx via Jupiter
        tx_hash = f"sim_sell_{mint[:8]}_{int(time.time())}"
        del self._positions[mint]

        return TradeResult(
            success=True,
            tx_hash=tx_hash,
            action=TradeAction.SELL,
            amount_sol=pos["amount"],
        )

    async def _check_rug(self, token: TokenInfo) -> float:
        """Check rug pull risk. Returns 0.0 (safe) to 1.0 (definite rug)."""
        # Delegated to anti_rug module
        from solsniper.anti_rug.detector import RugDetector
        detector = RugDetector()
        return await detector.score(token)

    async def _check_honeypot(self, token: TokenInfo) -> bool:
        """Check if token is a honeypot (can buy but can't sell)."""
        from solsniper.anti_rug.detector import RugDetector
        detector = RugDetector()
        return await detector.is_honeypot(token)

    def get_positions(self) -> dict:
        """Get all open positions."""
        return dict(self._positions)

    def get_stats(self) -> dict:
        """Get engine statistics."""
        return {
            "running": self._running,
            "active_snipes": self._active_snipes,
            "positions": len(self._positions),
            "tokens_seen": len(self._tokens_seen),
        }
