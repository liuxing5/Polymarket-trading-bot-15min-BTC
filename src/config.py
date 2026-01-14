"""
config.py
Loads settings from .env and normalizes variable names.

Supports BOTH:
 - API_KEY, API_SECRET, API_PASSPHRASE, PRIVATE_KEY
 - POLYMARKET_API_KEY, POLYMARKET_API_SECRET, POLYMARKET_API_PASSPHRASE, POLYMARKET_PRIVATE_KEY
"""

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


def _get(key: str, default=None):
    """Fetch from .env, supporting fallback POLYMARKET_ keys."""
    # Primary key
    v = os.getenv(key)
    if v not in (None, ""):
        return v

    # Auto fallback mapping (API_KEY → POLYMARKET_API_KEY)
    pm_key = f"POLYMARKET_{key}"
    v2 = os.getenv(pm_key)
    if v2 not in (None, ""):
        return v2

    return default


@dataclass
class Settings:
    # Core creds
    api_key: str
    api_secret: str
    api_passphrase: str
    private_key: str
    signature_type: int
    funder: str

    # Market logic
    # market_slug: str
    market_keyword: str

    order_size: float
    target_pair_cost: float
    cooldown_seconds: int

    # Mode flags
    dry_run: bool
    verbose: bool
    use_rich_output: bool
    use_wss: bool

    # Risk control
    max_daily_loss: float
    max_position_size: float
    max_trades_per_day: int
    min_balance_required: float
    max_balance_utilization: float

    # Stats
    enable_stats: bool
    trade_log_file: str
    sim_balance: float

    # Websocket
    ws_url: str


def load_settings():
    return Settings(
        # --- credentials (support dual names) ---
        api_key=_get("API_KEY", ""),
        api_secret=_get("API_SECRET", ""),
        api_passphrase=_get("API_PASSPHRASE", ""),
        private_key=_get("PRIVATE_KEY", ""),
        signature_type=int(_get("SIGNATURE_TYPE", "0")),
        funder=_get("FUNDER", ""),

        # --- market basics ---
        # market_slug=_get("MARKET_SLUG", ""),
        market_keyword=_get("MARKET_KEYWORD", "BTC"),
        order_size=float(_get("ORDER_SIZE", 1)),
        target_pair_cost=float(_get("TARGET_PAIR_COST", 1.00)),
        cooldown_seconds=int(_get("COOLDOWN_SECONDS", 2)),

        # --- mode flags ---
        dry_run=_get("DRY_RUN", "True").lower() == "true",
        verbose=_get("VERBOSE", "False").lower() == "true",
        use_rich_output=_get("USE_RICH_OUTPUT", "False").lower() == "true",
        use_wss=_get("USE_WSS", "False").lower() == "true",

        # --- risk ---
        max_daily_loss=float(_get("MAX_DAILY_LOSS", 0)),
        max_position_size=float(_get("MAX_POSITION_SIZE", 0)),
        max_trades_per_day=int(_get("MAX_TRADES_PER_DAY", 0)),
        min_balance_required=float(_get("MIN_BALANCE_REQUIRED", 0)),
        max_balance_utilization=float(_get("MAX_BALANCE_UTILIZATION", 1.0)),

        # --- stats ---
        enable_stats=_get("ENABLE_STATS", "False").lower() == "true",
        trade_log_file=_get("TRADE_LOG_FILE", "trade_log.csv"),
        sim_balance=float(_get("SIM_BALANCE", 100.0)),

        # --- Websocket ---
        ws_url=_get("WS_URL", "wss://clob.polymarket.com/ws"),
    )
