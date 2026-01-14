"""
statistics.py

Lightweight trade statistics logger & summary generator.
No dependency on Pandas to avoid blocking latency / install complexity.

Features:
✔ append-only log writes
✔ tracks trades in-memory
✔ safe file writes (never crash the bot)
✔ summary helpers for UI/logs
"""

import csv
import os
import time
from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class TradeRecord:
    timestamp: float
    market_slug: str
    price_up: float
    price_down: float
    total_cost: float
    order_size: float
    expected_profit: float
    order_ids: Optional[List[str]] = None
    market_result: Optional[str] = None


@dataclass
class StatsSnapshot:
    total_trades: int
    total_invested: float
    total_expected_profit: float
    total_actual_profit: float
    win_rate: float
    average_profit_per_trade: float
    average_profit_percentage: float


class StatisticsTracker:
    def __init__(self, log_file: Optional[str] = None):
        self.log_file = log_file
        self.trades: List[TradeRecord] = []

        if log_file:
            self._ensure_header()

    def _ensure_header(self):
        """Ensure CSV logfile has a header row."""
        try:
            if not os.path.exists(self.log_file):
                with open(self.log_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        "timestamp",
                        "market_slug",
                        "price_up",
                        "price_down",
                        "total_cost",
                        "order_size",
                        "expected_profit",
                        "order_ids",
                        "market_result",
                    ])
        except Exception:
            pass  # never crash the bot

    def record_trade(
        self,
        market_slug: str,
        price_up: float,
        price_down: float,
        total_cost: float,
        order_size: float,
        expected_profit: Optional[float] = None,
        order_ids: Optional[List[str]] = None,
        filled: bool = True,
    ) -> TradeRecord:
        """
        Store trade in memory + append to CSV.
        """
        ts = time.time()
        exp_profit = expected_profit if expected_profit is not None else (order_size * 2 - total_cost * order_size)

        rec = TradeRecord(
            timestamp=ts,
            market_slug=market_slug,
            price_up=price_up,
            price_down=price_down,
            total_cost=total_cost,
            order_size=order_size,
            expected_profit=exp_profit,
            order_ids=order_ids,
        )
        self.trades.append(rec)

        if self.log_file:
            try:
                with open(self.log_file, "a", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow([
                        rec.timestamp,
                        rec.market_slug,
                        rec.price_up,
                        rec.price_down,
                        rec.total_cost,
                        rec.order_size,
                        rec.expected_profit,
                        ";".join(rec.order_ids or []),
                        rec.market_result or "",
                    ])
            except Exception:
                pass  # skip file errors silently

        return rec

    def get_stats(self) -> StatsSnapshot:
        """
        Compute summary statistics from in-memory trades.
        """
        n = len(self.trades)
        if n == 0:
            return StatsSnapshot(
                total_trades=0,
                total_invested=0,
                total_expected_profit=0,
                total_actual_profit=0,
                win_rate=0,
                average_profit_per_trade=0,
                average_profit_percentage=0,
            )

        total_invested = sum(t.total_cost * t.order_size for t in self.trades)
        total_expected_profit = sum(t.expected_profit for t in self.trades)

        # If the market_result was added later, estimate:
        total_actual_profit = 0
        wins = 0
        for t in self.trades:
            # crude win definition: expected profit > 0
            if t.expected_profit > 0:
                wins += 1
                total_actual_profit += t.expected_profit

        win_rate = (wins / n) * 100.0
        avg_profit_trade = total_expected_profit / n
        avg_profit_pct = (avg_profit_trade / (total_invested / n)) * 100.0 if total_invested else 0.0

        return StatsSnapshot(
            total_trades=n,
            total_invested=total_invested,
            total_expected_profit=total_expected_profit,
            total_actual_profit=total_actual_profit,
            win_rate=win_rate,
            average_profit_per_trade=avg_profit_trade,
            average_profit_percentage=avg_profit_pct,
        )
