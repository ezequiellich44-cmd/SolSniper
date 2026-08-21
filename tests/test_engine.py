"""Tests for SolSniper core engine."""

import pytest
from solsniper.core.engine import SniperEngine, SniperConfig, TokenInfo, Source, TradeAction
from solsniper.anti_rug.detector import RugDetector
from solsniper.copytrade.engine import CopyTrader, CopyTradeConfig
from solsniper.jito.optimizer import JitoOptimizer


@pytest.fixture
def config():
    return SniperConfig(
        private_key="",
        buy_amount_sol=0.1,
        slippage_bps=500,
        use_jito=True,
        detect_rugs=True,
    )


@pytest.fixture
def engine(config):
    return SniperEngine(config)


@pytest.fixture
def sample_token():
    return TokenInfo(
        mint="So11111111111111111111111111111111111111112",
        name="TestCoin",
        symbol="TEST",
        source=Source.PUMP_FUN,
        initial_liquidity=5.0,
    )


# ── Engine Tests ─────────────────────────────────────────────

def test_engine_init(engine):
    assert engine.config is not None
    assert engine._running is False
    assert engine._active_snipes == 0


def test_engine_stats(engine):
    stats = engine.get_stats()
    assert stats["running"] is False
    assert stats["active_snipes"] == 0
    assert stats["positions"] == 0


@pytest.mark.asyncio
async def test_snipe_no_wallet(engine, sample_token):
    result = await engine.snipe(sample_token)
    assert result.success is False
    assert "No wallet configured" in result.error


# ── Anti-Rug Tests ───────────────────────────────────────────

@pytest.mark.asyncio
async def test_rug_detector_safe(sample_token):
    detector = RugDetector()
    score = await detector.score(sample_token)
    assert 0.0 <= score <= 1.0


@pytest.mark.asyncio
async def test_rug_detector_honeypot_check(sample_token):
    detector = RugDetector()
    is_honeypot = await detector.is_honeypot(sample_token)
    assert isinstance(is_honeypot, bool)


def test_rug_patterns():
    detector = RugDetector()
    detector.add_rug_pattern("scam1", was_rug=True)
    detector.add_rug_pattern("legit1", was_rug=False)
    stats = detector.get_pattern_stats()
    assert stats["known_rugs"] == 1
    assert stats["legitimate"] == 1


# ── Copy Trading Tests ──────────────────────────────────────

def test_copy_trader_add_wallet():
    config = CopyTradeConfig(min_score=50)
    trader = CopyTrader(config)
    ws = trader.add_wallet("wallet123", tags=["whale"])
    assert ws.address == "wallet123"
    assert "whale" in ws.tags


def test_copy_trader_blacklist():
    config = CopyTradeConfig(blacklist=["badwallet"])
    trader = CopyTrader(config)
    with pytest.raises(ValueError):
        trader.add_wallet("badwallet")


def test_copy_trader_should_copy():
    config = CopyTradeConfig(min_score=60)
    trader = CopyTrader(config)
    ws = trader.add_wallet("wallet123")
    ws.score = 70
    assert trader.should_copy("wallet123") is True

    ws.score = 40
    assert trader.should_copy("wallet123") is False


def test_copy_trader_top_wallets():
    config = CopyTradeConfig()
    trader = CopyTrader(config)
    for i in range(5):
        ws = trader.add_wallet(f"wallet{i}")
        ws.score = i * 20

    top = trader.get_top_wallets(3)
    assert len(top) == 3
    assert top[0].score >= top[1].score >= top[2].score


# ── Jito Tests ──────────────────────────────────────────────

@pytest.mark.asyncio
async def test_jito_congestion():
    optimizer = JitoOptimizer()
    congestion = await optimizer.get_congestion()
    assert congestion.congestion_level in ("low", "medium", "high", "extreme")
    assert congestion.recommended_tip_lamports > 0


def test_jito_tip_calculation():
    optimizer = JitoOptimizer()
    tip = optimizer.calculate_optimal_tip(priority=1)
    assert tip > 0
    assert isinstance(tip, int)


@pytest.mark.asyncio
async def test_jito_submit_bundle():
    optimizer = JitoOptimizer()
    bundle = await optimizer.submit_bundle(["tx1", "tx2"], priority=1)
    assert bundle.bundle_id.startswith("jito_")
    assert bundle.tip_lamports > 0
