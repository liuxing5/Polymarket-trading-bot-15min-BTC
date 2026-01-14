"""
risk_manager.py
Risk controls for BTC 15M arbitrage bot.

Features:
✔ Daily max loss
✔ Daily max trades
✔ Position size limit
✔ Balance utilization guard
✔ Tracks expected profit (and allows resolved replacement)
✔ Auto day rollover
✔ Zero-runtime errors when limits unset
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class RiskLimits:
    max_daily_loss: Optional[float] = None        # Stop if netPnL < -max_loss
    max_trades_per_day: Optional[int] = None     # Block trades after hitting limit
    max_position_size: Optional[float] = None    # Per-trade cap
    min_balance_required: float = 0.0             # Must hold at least this much USDC
    max_balance_utilization: float = 1.0          # 0.5 => never spend >50% of wallet per trade


@dataclass
class DailyRiskState:
    date: str
    trades_count: int = 0
    net_pnl: float = 0.0  # running PnL (expected or realized)
    invested: float = 0.0


class RiskManager:
    def __init__(self, limits: RiskLimits):
        self.limits = limits
        today = datetime.utcnow().strftime("%Y-%m-%d")
        self.state = DailyRiskState(date=today)

    # -----------------------------------------------------------
    # HELPER: Day Reset
    # -----------------------------------------------------------
    def _rollover_if_needed(self):
        today = datetime.utcnow().strftime("%Y-%m-%d")
        if self.state.date != today:
            self.state = DailyRiskState(date=today)

    # -----------------------------------------------------------
    # MAIN CHECK
    # -----------------------------------------------------------
    def can_trade(self, trade_size: float, current_balance: float):
        """
        Returns:
            (True, '') if allowed
            (False, 'reason') if blocked
        """
        self._rollover_if_needed()

        # Require minimum balance
        if current_balance < self.limits.min_balance_required:
            return False, (
                f"Balance too low: {current_balance:.2f} < "
                f"{self.limits.min_balance_required:.2f}"
            )

        # Max utilization guard
        max_spend = current_balance * float(self.limits.max_balance_utilization)
        if trade_size > max_spend:
            return False, (
                f"Trade cost {trade_size:.2f} > utilization "
                f"limit {max_spend:.2f}"
            )

        # Max trades/day
        if self.limits.max_trades_per_day is not None:
            if self.state.trades_count >= self.limits.max_trades_per_day:
                return False, (
                    f"Hit daily trade cap "
                    f"{self.state.trades_count}/{self.limits.max_trades_per_day}"
                )

        # Per trade max position
        if self.limits.max_position_size is not None:
            if trade_size > self.limits.max_position_size:
                return False, (
                    f"Trade too large: {trade_size:.2f} > "
                    f"{self.limits.max_position_size:.2f}"
                )

        # Daily loss stop
        if self.limits.max_daily_loss is not None:
            if self.state.net_pnl < -abs(self.limits.max_daily_loss):
                return False, (
                    f"Daily PnL {self.state.net_pnl:.2f} < "
                    f"limit -{abs(self.limits.max_daily_loss):.2f}"
                )

        return True, ""

    # -----------------------------------------------------------
    # STATE UPDATE
    # -----------------------------------------------------------
    def record_trade_result(self, profit: float):
        """
        Called when a trade is executed successfully.
        Profit passed here is EXPECTED profit until the market settles.
        """
        self._rollover_if_needed()
        self.state.trades_count += 1
        self.state.net_pnl += profit

    # Optionally replace expected PnL with actual resolution
    def adjust_actual_pnl(self, realized_profit: float):
        """
        Call this when a market resolves.
        """
        self._rollover_if_needed()
        self.state.net_pnl += realized_profit

    # -----------------------------------------------------------
    # EXTERNAL SNAPSHOT
    # -----------------------------------------------------------
    def get_daily_stats(self):
        """
        For logging / display
        """
        self._rollover_if_needed()
        return {
            "date": self.state.date,
            "trades": self.state.trades_count,
            "net_pnl": self.state.net_pnl,
        }
