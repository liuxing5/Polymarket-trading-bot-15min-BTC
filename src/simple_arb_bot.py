# ======================= simple_arb_bot.py =======================
"""
BTC 15-Min Arbitrage Bot
Enhanced by ChatGPT:
✔ VWAP worst-price cost calculation
✔ Risk throttling + fail_count backoff
✔ Redeem auto conversion
✔ GracefulShutdown fixed
✔ REST/WSS unified logic
"""

import asyncio
import logging
import time
from datetime import datetime
from typing import Optional

from .config import load_settings
from .config_validator import ConfigValidator
from .logger import setup_logging, print_header, print_error
from .risk_manager import RiskManager, RiskLimits
from .statistics import StatisticsTracker
from .trading import (
    get_client, place_order, cancel_orders, get_positions,
    place_orders_fast, extract_order_id, wait_for_terminal_order,
    has_redeemable, redeem_all,
)
from .utils import GracefulShutdown
from .lookup import auto_wait_market
from .wss_market import MarketWssClient

logger = logging.getLogger(__name__)


class SimpleArbitrageBot:
    def __init__(self, settings):
        self.settings = settings
        self.client = get_client(settings)

        # Stats
        self.trades_executed = 0
        self.positions = []
        self.total_invested = 0.0
        self.total_shares_bought = 0
        self.cached_balance = None

        # Risk & tracking
        self.risk_manager = RiskManager(
            RiskLimits(
                max_daily_loss=settings.max_daily_loss,
                max_trades_per_day=settings.max_trades_per_day,
                max_position_size=settings.max_position_size,
                min_balance_required=settings.min_balance_required,
                max_balance_utilization=settings.max_balance_utilization,
            )
        )

        self.fail_count = 0
        self._last_execution_ts = 0.0

        # Market lookup

        mkt = auto_wait_market(keyword=getattr(settings, "market_keyword", "btc"), retry_seconds=30)

        self.yes_token_id = mkt["yes_token_id"]
        self.no_token_id = mkt["no_token_id"]

        if settings.dry_run:
            self.sim_balance = float(settings.sim_start_balance)

    def get_balance(self):
        if self.cached_balance is not None:
            return self.cached_balance
        wallets = self.client.get("/wallet").json()
        return float(wallets["balances"].get("USDC", 0))

    def get_order_book(self, token_id):
        res = self.client.get(f"/orderbook/{token_id}").json()
        return {
            "asks": res.get("asks", []),
            "bids": res.get("bids", []),
            "best_bid": res.get("bestBid"),
            "best_ask": res.get("bestAsk"),
        }

    def _compute_buy_fill(self, asks, size):
        filled = 0
        cost = 0.0
        worst = None
        for lvl in asks:
            px = float(lvl["px"])
            sz = float(lvl["sz"])
            take = min(size - filled, sz)
            filled += take
            cost += take * px
            worst = px
            if filled >= size:
                break
        if filled < size:
            return None
        return {
            "vwap": cost / size,
            "worst": worst,
        }

    def check_arbitrage(self, up_book=None, down_book=None):
        up_book = up_book or self.get_order_book(self.yes_token_id)
        down_book = down_book or self.get_order_book(self.no_token_id)

        asks_up = up_book.get("asks", [])
        asks_down = down_book.get("asks", [])

        size = float(self.settings.order_size)
        fill_up = self._compute_buy_fill(asks_up, size)
        fill_down = self._compute_buy_fill(asks_down, size)
        if not fill_up or not fill_down:
            return None

        price_up = fill_up["worst"]
        price_down = fill_down["worst"]
        raw_cost = price_up + price_down
        buffer = 0.004
        adj_cost = raw_cost * (1 + buffer)

        if adj_cost > self.settings.target_pair_cost:
            return None

        expected_payout = size * 2
        investment = adj_cost * size
        expected_profit = expected_payout - investment

        return {
            "price_up": price_up,
            "price_down": price_down,
            "vwap_up": fill_up["vwap"],
            "vwap_down": fill_down["vwap"],
            "raw_cost": raw_cost,
            "total_cost": adj_cost,
            "order_size": size,
            "expected_profit": expected_profit,
            "total_investment": investment,
            "profit_pct": (1 - adj_cost) * 100,
        }
    def execute_arbitrage(self, opp):
        """Execute arbitrage with full safeguards."""

        # Too many failures? Pause
        if self.fail_count >= 3:
            logger.warning("⏸ Too many failures (>=3). Cooling down for 60 seconds.")
            time.sleep(60)
            self.fail_count = 0

        now = time.time()
        cd = float(self.settings.cooldown_seconds)
        if cd and (now - self._last_execution_ts) < cd:
            logger.info(f"Cooldown active ({cd}s)")
            return
        self._last_execution_ts = now

        # Dry run branch
        if self.settings.dry_run:
            if self.sim_balance < opp["total_investment"]:
                logger.error("❌ Insufficient sim balance.")
                self.fail_count += 1
                return
            self.sim_balance -= opp["total_investment"]
            self.positions.append(opp)
            self.trades_executed += 1
            self.total_invested += opp["total_investment"]
            return

        # Real mode
        bal = self.get_balance()
        need = opp["total_investment"]
        # Slight overshoot to avoid dust-margin insufficiency
        if bal < need * 1.1:
            logger.error(f"❌ Balance too low. Need {need:.2f}, have {bal:.2f}")
            self.fail_count += 1
            return

        # Risk manager
        ok, reason = self.risk_manager.can_trade(
            trade_size=need, current_balance=bal
        )
        if not ok:
            logger.warning(f"⚠ Trade blocked: {reason}")
            self.fail_count += 1
            return

        try:
            # Submit both
            orders = [
                {"side": "BUY", "token_id": self.yes_token_id,
                 "price": opp["price_up"], "size": opp["order_size"]},
                {"side": "BUY", "token_id": self.no_token_id,
                 "price": opp["price_down"], "size": opp["order_size"]},
            ]

            res = place_orders_fast(self.settings, orders, order_type="GTC")
            up_id = extract_order_id(res[0])
            dn_id = extract_order_id(res[1])

            if not up_id or not dn_id:
                logger.error("❌ Could not extract order IDs.")
                self.fail_count += 1
                return

            req = opp["order_size"]
            up_state = wait_for_terminal_order(self.settings, up_id, requested_size=req)
            dn_state = wait_for_terminal_order(self.settings, dn_id, requested_size=req)

            up_ok = up_state.get("filled_size", 0) >= req
            dn_ok = dn_state.get("filled_size", 0) >= req

            # Partial fill logic
            if not (up_ok and dn_ok):
                logger.error("❌ Partial fill – attempting unwind")
                try:
                    cancel_orders(self.settings, [up_id, dn_id])
                except:
                    pass
                self.fail_count += 1
                return

            # Success
            self.fail_count = 0
            self.trades_executed += 1
            self.total_invested += opp["total_investment"]
            self.positions.append(opp)
            self.cached_balance = None  # force re-fetch next time

            # Book assumed PnL (risk manager sees it)
            self.risk_manager.record_trade_result(opp["expected_profit"])

            logger.info(f"🎯 Arbitrage filled: est profit={opp['expected_profit']:.3f}")

        except Exception as e:
            logger.error(f"Execution error: {e}")
            self.fail_count += 1
            return

    # ---------------------------
    # Single cycle REST
    # ---------------------------
    def run_once(self) -> bool:
        up = self.get_order_book(self.yes_token_id)
        down = self.get_order_book(self.no_token_id)
        opp = self.check_arbitrage(up, down)
        if opp:
            self.execute_arbitrage(opp)
            return True
        self.fail_count += 1
        return False

    async def run_once_async(self) -> bool:
        up = self.get_order_book(self.yes_token_id)
        down = self.get_order_book(self.no_token_id)
        opp = self.check_arbitrage(up, down)
        if opp:
            self.execute_arbitrage(opp)
            return True
        self.fail_count += 1
        return False

    # ---------------------------
    # main monitor loop
    # ---------------------------
    async def monitor(self, interval_seconds=0):
        use_wss = getattr(self.settings, "use_wss", False)
        logger.info(f"📡 Monitor started - WSS={use_wss}")

        if use_wss:
            client = MarketWssClient(
                ws_base_url=self.settings.ws_url,
                asset_ids=[self.yes_token_id, self.no_token_id]
            )
            async for asset_id, event in client.run():
                opp = self.check_arbitrage()
                if opp:
                    self.execute_arbitrage(opp)

                # Auto redeem
                try:
                    if has_redeemable(self.settings):
                        logger.info("💰 Redeemable tokens detected — redeeming…")
                        res = redeem_all(self.settings)
                        logger.info(f"Redeem result: {res}")
                except Exception as e:
                    logger.error(f"[redeem] {e}")

                if GracefulShutdown.SHUTDOWN:
                    logger.warning("👋 Shutdown detected")
                    return
        else:
            while not GracefulShutdown.SHUTDOWN:
                try:
                    opp = self.check_arbitrage()
                    if opp:
                        self.execute_arbitrage(opp)

                    # Auto redeem
                    try:
                        if has_redeemable(self.settings):
                            logger.info("💰 Redeemable tokens detected — redeeming…")
                            res = redeem_all(self.settings)
                            logger.info(f"Redeem result: {res}")
                    except Exception as e:
                        logger.error(f"[redeem] {e}")

                except Exception as e:
                    logger.error(f"[monitor] {e}")

                if interval_seconds > 0:
                    await asyncio.sleep(interval_seconds)

# ---------------------------
# Main
# ---------------------------
async def main():
    settings = load_settings()
    setup_logging(verbose=settings.verbose, use_rich=settings.use_rich_output)

    if not ConfigValidator.validate_and_print(settings):
        print_error("Config error.")
        return

    print_header("🚀 BTC 15-Min Arbitrage Bot")

    bot = SimpleArbitrageBot(settings)
    await bot.monitor(interval_seconds=0)

if __name__ == "__main__":
    asyncio.run(main())
