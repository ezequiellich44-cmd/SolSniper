"""Hosted API service — the paywall backend.

This is how we make money:
1. Free tier: basic sniper, limited features
2. Pro tier: full features, higher limits
3. Elite tier: everything + API access + priority

The hosted version handles:
- RPC infrastructure (expensive)
- Jito bundle submission (requires stake)
- Wallet management (secure key storage)
- Rate limiting per license tier
"""

from __future__ import annotations

import hashlib
import time
from dataclasses import dataclass, field
from typing import Optional

from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel


# ── License Tiers ──────────────────────────────────────────────

TIER_LIMITS = {
    "free": {
        "snipes_per_day": 5,
        "copy_wallets": 0,
        "jito_bundles": False,
        "anti_rug_basic": True,
        "anti_rug_ml": False,
        "telegram_alerts": False,
        "api_access": False,
        "rpc_calls_per_day": 100,
    },
    "pro": {
        "snipes_per_day": 50,
        "copy_wallets": 5,
        "jito_bundles": True,
        "anti_rug_basic": True,
        "anti_rug_ml": True,
        "telegram_alerts": True,
        "api_access": False,
        "rpc_calls_per_day": 1000,
    },
    "elite": {
        "snipes_per_day": -1,  # unlimited
        "copy_wallets": 20,
        "jito_bundles": True,
        "anti_rug_basic": True,
        "anti_rug_ml": True,
        "telegram_alerts": True,
        "api_access": True,
        "rpc_calls_per_day": -1,  # unlimited
    },
}

TIER_PRICES = {
    "pro": {"monthly": 49, "lifetime": 299},
    "elite": {"monthly": 99, "lifetime": 499},
}

WALLETS = {
    "solana": "3fZSMAyCEMhZwWiynbJDjoYNUT97aiV9BLzoUNroEMAz",
    "evm": "0x4Ed4D0750453C027FA8398067d5af980Bcc9B6eD",
}


# ── Models ──────────────────────────────────────────────────────

class LicenseKey(BaseModel):
    key: str
    tier: str
    created_at: float
    expires_at: float | None = None


class SnipeRequest(BaseModel):
    mint: str
    source: str = "pump.fun"
    amount_sol: float = 0.1
    slippage_bps: int = 500


class SnipeResponse(BaseModel):
    success: bool
    tx_hash: str | None = None
    error: str | None = None
    tier: str = "free"
    remaining_snipes: int = 0


class CopyWalletRequest(BaseModel):
    wallet: str
    max_position_sol: float = 0.5


class UsageStats(BaseModel):
    tier: str
    snipes_today: int
    snipes_remaining: int
    rpc_calls_today: int
    rpc_calls_remaining: int
    copy_wallets_used: int
    copy_wallets_remaining: int


# ── API App ─────────────────────────────────────────────────────

app = FastAPI(
    title="SolSniper API",
    description="Premium Solana sniper bot — hosted service",
    version="0.1.0",
)

# In-memory stores (production: Redis + PostgreSQL)
_licenses: dict[str, LicenseKey] = {}
_usage: dict[str, dict] = {}  # license_key -> {snipes_today, rpc_calls_today, ...}


def _get_tier(license_key: str | None) -> str:
    """Get tier from license key."""
    if not license_key:
        return "free"
    key_data = _licenses.get(license_key)
    if not key_data:
        return "free"
    if key_data.expires_at and time.time() > key_data.expires_at:
        return "free"
    return key_data.tier


def _check_usage(license_key: str, tier: str) -> dict:
    """Check and update usage limits."""
    if license_key not in _usage:
        _usage[license_key] = {
            "snipes_today": 0,
            "rpc_calls_today": 0,
            "copy_wallets_used": 0,
            "last_reset": time.time(),
        }

    usage = _usage[license_key]
    limits = TIER_LIMITS[tier]

    # Reset daily counters if needed
    if time.time() - usage["last_reset"] > 86400:
        usage["snipes_today"] = 0
        usage["rpc_calls_today"] = 0
        usage["last_reset"] = time.time()

    snipes_remaining = limits["snipes_per_day"] - usage["snipes_today"]
    rpc_remaining = limits["rpc_calls_per_day"] - usage["rpc_calls_today"]
    if limits["rpc_calls_per_day"] == -1:
        rpc_remaining = -1

    return {
        "snipes_remaining": max(0, snipes_remaining) if snipes_remaining != -1 else -1,
        "rpc_remaining": max(0, rpc_remaining) if rpc_remaining != -1 else -1,
        "copy_wallets_remaining": limits["copy_wallets"] - usage["copy_wallets_used"],
    }


# ── Endpoints ───────────────────────────────────────────────────

@app.get("/")
async def root():
    return {
        "name": "SolSniper API",
        "version": "0.1.0",
        "docs": "/docs",
        "pricing": TIER_PRICES,
    }


@app.get("/pricing")
async def pricing():
    """Get pricing information."""
    return {
        "tiers": TIER_PRICES,
        "wallets": WALLETS,
        "features": TIER_LIMITS,
    }


@app.post("/snipe", response_model=SnipeResponse)
async def snipe(
    request: SnipeRequest,
    authorization: str | None = Header(None),
):
    """Execute a snipe trade. Requires valid license key."""
    license_key = authorization.replace("Bearer ", "") if authorization else None
    tier = _get_tier(license_key)
    usage = _check_usage(license_key, tier)

    if usage["snipes_remaining"] == 0:
        raise HTTPException(
            status_code=429,
            detail={
                "error": "Daily snipe limit reached",
                "tier": tier,
                "upgrade": "https://github.com/ezequiellich44-cmd/SolSniper#pricing",
            },
        )

    # Execute snipe (in production: call sniper engine)
    # For now: simulated
    _usage[license_key]["snipes_today"] += 1

    return SnipeResponse(
        success=True,
        tx_hash=f"sim_{request.mint[:8]}_{int(time.time())}",
        tier=tier,
        remaining_snipes=usage["snipes_remaining"] - 1,
    )


@app.get("/usage", response_model=UsageStats)
async def get_usage(authorization: str | None = Header(None)):
    """Get current usage stats."""
    license_key = authorization.replace("Bearer ", "") if authorization else None
    tier = _get_tier(license_key)
    usage = _check_usage(license_key, tier)
    limits = TIER_LIMITS[tier]

    return UsageStats(
        tier=tier,
        snipes_today=_usage.get(license_key, {}).get("snipes_today", 0),
        snipes_remaining=usage["snipes_remaining"],
        rpc_calls_today=_usage.get(license_key, {}).get("rpc_calls_today", 0),
        rpc_calls_remaining=usage["rpc_remaining"],
        copy_wallets_used=_usage.get(license_key, {}).get("copy_wallets_used", 0),
        copy_wallets_remaining=usage["copy_wallets_remaining"],
    )


@app.post("/copy-wallet")
async def add_copy_wallet(
    request: CopyWalletRequest,
    authorization: str | None = Header(None),
):
    """Add a wallet to copy trade."""
    license_key = authorization.replace("Bearer ", "") if authorization else None
    tier = _get_tier(license_key)

    if tier == "free":
        raise HTTPException(
            status_code=403,
            detail={
                "error": "Copy trading requires Pro or Elite tier",
                "upgrade": "https://github.com/ezequiellich44-cmd/SolSniper#pricing",
            },
        )

    usage = _check_usage(license_key, tier)
    if usage["copy_wallets_remaining"] <= 0:
        raise HTTPException(
            status_code=429,
            detail={"error": "Copy wallet limit reached for your tier"},
        )

    _usage[license_key]["copy_wallets_used"] += 1

    return {"success": True, "wallet": request.wallet, "tier": tier}


@app.get("/health")
async def health():
    return {"status": "ok", "version": "0.1.0"}
