"""
config_validator.py

Validate environment values loaded into Settings() and warn
users when config is unsafe or missing.

Not strict enough to crash on minor issues,
but prevents dangerous misconfiguration.
"""

from .logger import print_error, print_warning, print_success
from .config import Settings


class ConfigValidator:

    REQUIRED = [
        "private_key",
        "api_key",
        "api_secret",
        "api_passphrase",
    ]

    @staticmethod
    def validate_and_print(settings: Settings) -> bool:
        """
        Validate loaded config and print guidance.
        Returns:
            True if config acceptable, False if critical failure.
        """

        ok = True

        # ===== 1. REQUIRED KEYS =====
        missing = []
        for key in ConfigValidator.REQUIRED:
            if not getattr(settings, key):
                missing.append(key)

        if missing and not settings.dry_run:
            print_error(f"Missing required config keys: {', '.join(missing)}")
            print_warning("Real trading disabled until API keys are provided!")
            ok = False

        # ===== 2. Trading Parameters =====

        if settings.order_size <= 0:
            print_error("ORDER_SIZE must be > 0")
            ok = False

        if not (0.0 < settings.target_pair_cost <= 1.0):
            print_error("TARGET_PAIR_COST must be between 0 and 1")
            ok = False

        if settings.cooldown_seconds < 0:
            print_error("COOLDOWN_SECONDS cannot be negative")
            ok = False

        # ===== 3. Risk Settings =====

        if settings.max_balance_utilization > 1.0:
            print_warning("MAX_BALANCE_UTILIZATION > 1.0 detected — may overuse funds")

        if settings.max_daily_loss < 0:
            print_error("MAX_DAILY_LOSS must be >= 0")
            ok = False

        if settings.max_position_size < 0:
            print_error("MAX_POSITION_SIZE must be >= 0")
            ok = False

        if settings.max_trades_per_day < 0:
            print_error("MAX_TRADES_PER_DAY must be >= 0")
            ok = False

        if settings.min_balance_required < 0:
            print_error("MIN_BALANCE_REQUIRED must be >= 0")
            ok = False

        # ===== 4. Logging / Stats =====

        if settings.enable_stats and not settings.trade_log_file:
            print_warning("ENABLE_STATS is true but TRADE_LOG_FILE missing — logging disabled")

        # ===== 5. Websocket URL =====

        if settings.use_wss and not settings.ws_url:
            print_error("USE_WSS=True requires WS_URL")
            ok = False

        # ===== 6. Dry-run Mode =====

        if settings.dry_run:
            print_success("Dry-run mode enabled: no real trades will execute")

        # ===== 7. Final verdict =====

        if ok:
            print_success("Configuration validated successfully ✔")
        else:
            print_error("Configuration validation failed ❌")

        return ok
