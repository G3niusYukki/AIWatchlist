"""
Backtesting Module
Simulate historical signal performance against price movements
"""

import asyncio
import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
from enum import Enum

from .models import SignalType


@dataclass
class BacktestTrade:
    entry_date: datetime
    exit_date: Optional[datetime]
    entry_price: float
    exit_price: Optional[float]
    signal: SignalType
    shares: int
    pnl: float = 0.0
    pnl_pct: float = 0.0
    holding_days: int = 0


@dataclass
class BacktestResult:
    ticker: str
    start_date: datetime
    end_date: datetime
    initial_capital: float
    final_capital: float
    total_return: float
    total_return_pct: float
    benchmark_return_pct: float
    trades: list[BacktestTrade]
    winning_trades: int
    losing_trades: int
    win_rate: float
    avg_win_pct: float
    avg_loss_pct: float
    max_drawdown: float
    sharpe_ratio: float
    signals_generated: dict[str, int]

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "period": f"{self.start_date.strftime('%Y-%m-%d')} to {self.end_date.strftime('%Y-%m-%d')}",
            "initial_capital": round(self.initial_capital, 2),
            "final_capital": round(self.final_capital, 2),
            "total_return": round(self.total_return, 2),
            "total_return_pct": round(self.total_return_pct, 2),
            "benchmark_return_pct": round(self.benchmark_return_pct, 2),
            "alpha": round(self.total_return_pct - self.benchmark_return_pct, 2),
            "winning_trades": self.winning_trades,
            "losing_trades": self.losing_trades,
            "win_rate": round(self.win_rate, 2),
            "avg_win_pct": round(self.avg_win_pct, 2),
            "avg_loss_pct": round(self.avg_loss_pct, 2),
            "max_drawdown": round(self.max_drawdown, 2),
            "sharpe_ratio": round(self.sharpe_ratio, 2),
            "total_trades": len(self.trades),
            "signals_generated": self.signals_generated,
        }


class BacktestStrategy(Enum):
    SIGNAL_FOLLOW = "signal_follow"
    STRONG_BUY_ONLY = "strong_buy_only"
    BUY_AND_HOLD = "buy_and_hold"
    MEAN_REVERSION = "mean_reversion"


class Backtester:
    def __init__(
        self,
        initial_capital: float = 100000,
        strategy: BacktestStrategy = BacktestStrategy.SIGNAL_FOLLOW,
        position_size_pct: float = 0.1,
        stop_loss_pct: float = 0.1,
        take_profit_pct: float = 0.2,
        use_mock: bool = True,
    ):
        self.initial_capital = initial_capital
        self.strategy = strategy
        self.position_size_pct = position_size_pct
        self.stop_loss_pct = stop_loss_pct
        self.take_profit_pct = take_profit_pct
        self.use_mock = use_mock

    def _generate_mock_price_history(self, ticker: str, weeks: int) -> list[dict]:
        base_price = random.uniform(50, 500)
        prices = []
        current_price = base_price

        for i in range(weeks * 5):
            daily_change = random.gauss(0.001, 0.02)
            current_price *= 1 + daily_change
            current_price = max(current_price, 1)

            date = datetime.now() - timedelta(days=(weeks * 5 - i))

            prices.append(
                {
                    "date": date,
                    "open": current_price * random.uniform(0.98, 1.02),
                    "high": current_price * random.uniform(1.0, 1.05),
                    "low": current_price * random.uniform(0.95, 1.0),
                    "close": current_price,
                    "volume": random.randint(1000000, 50000000),
                }
            )

        return prices

    def _generate_mock_signals(
        self, weeks: int
    ) -> list[tuple[datetime, SignalType, float]]:
        signals = []
        signal_types = [
            SignalType.STRONG_BUY,
            SignalType.BUY,
            SignalType.HOLD,
            SignalType.SELL,
            SignalType.STRONG_SELL,
        ]
        weights = [0.1, 0.25, 0.35, 0.2, 0.1]

        for i in range(weeks):
            date = datetime.now() - timedelta(weeks=(weeks - i))
            signal = random.choices(signal_types, weights)[0]
            score = random.uniform(-2.5, 2.5)
            signals.append((date, signal, score))

        return signals

    async def run_backtest(
        self,
        ticker: str,
        weeks: int = 12,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> dict:
        end_date = end_date or datetime.now()
        start_date = start_date or (end_date - timedelta(weeks=weeks))

        price_history = self._generate_mock_price_history(ticker, weeks)
        signals = self._generate_mock_signals(weeks)

        trades = await self._simulate_trades(ticker, price_history, signals)
        result = self._calculate_metrics(
            ticker, trades, price_history, start_date, end_date
        )

        return result.to_dict()

    async def _simulate_trades(
        self,
        ticker: str,
        price_history: list[dict],
        signals: list[tuple[datetime, SignalType, float]],
    ) -> list[BacktestTrade]:
        trades = []
        capital = self.initial_capital
        position = 0
        entry_price = 0

        signal_map = {s[0].strftime("%Y-%W"): (s[1], s[2]) for s in signals}

        for i, bar in enumerate(price_history):
            week_key = bar["date"].strftime("%Y-%W")
            signal, score = signal_map.get(week_key, (SignalType.HOLD, 0))

            price = bar["close"]

            if position > 0:
                pnl_pct = (price - entry_price) / entry_price

                if pnl_pct <= -self.stop_loss_pct:
                    pnl = (price - entry_price) * position
                    capital += price * position
                    trades.append(
                        BacktestTrade(
                            entry_date=trades[-1].entry_date if trades else bar["date"],
                            exit_date=bar["date"],
                            entry_price=entry_price,
                            exit_price=price,
                            signal=signal,
                            shares=position,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            holding_days=i,
                        )
                    )
                    position = 0
                    entry_price = 0
                    continue

                if pnl_pct >= self.take_profit_pct:
                    pnl = (price - entry_price) * position
                    capital += price * position
                    trades.append(
                        BacktestTrade(
                            entry_date=trades[-1].entry_date if trades else bar["date"],
                            exit_date=bar["date"],
                            entry_price=entry_price,
                            exit_price=price,
                            signal=signal,
                            shares=position,
                            pnl=pnl,
                            pnl_pct=pnl_pct,
                            holding_days=i,
                        )
                    )
                    position = 0
                    entry_price = 0
                    continue

            if self.strategy == BacktestStrategy.SIGNAL_FOLLOW:
                if signal in [SignalType.STRONG_BUY, SignalType.BUY] and position == 0:
                    shares = int((capital * self.position_size_pct) / price)
                    if shares > 0:
                        position = shares
                        entry_price = price
                        capital -= price * shares
                        trades.append(
                            BacktestTrade(
                                entry_date=bar["date"],
                                exit_date=None,
                                entry_price=price,
                                exit_price=None,
                                signal=signal,
                                shares=shares,
                            )
                        )

                elif (
                    signal in [SignalType.SELL, SignalType.STRONG_SELL] and position > 0
                ):
                    pnl = (price - entry_price) * position
                    pnl_pct = (price - entry_price) / entry_price
                    capital += price * position
                    trades[-1].exit_date = bar["date"]
                    trades[-1].exit_price = price
                    trades[-1].pnl = pnl
                    trades[-1].pnl_pct = pnl_pct
                    trades[-1].holding_days = i
                    position = 0
                    entry_price = 0

            elif self.strategy == BacktestStrategy.STRONG_BUY_ONLY:
                if signal == SignalType.STRONG_BUY and position == 0:
                    shares = int((capital * self.position_size_pct * 2) / price)
                    if shares > 0:
                        position = shares
                        entry_price = price
                        capital -= price * shares
                        trades.append(
                            BacktestTrade(
                                entry_date=bar["date"],
                                exit_date=None,
                                entry_price=price,
                                exit_price=None,
                                signal=signal,
                                shares=shares,
                            )
                        )

        if position > 0 and price_history:
            final_price = price_history[-1]["close"]
            pnl = (final_price - entry_price) * position
            pnl_pct = (final_price - entry_price) / entry_price
            capital += final_price * position
            if trades:
                trades[-1].exit_date = price_history[-1]["date"]
                trades[-1].exit_price = final_price
                trades[-1].pnl = pnl
                trades[-1].pnl_pct = pnl_pct

        return trades

    def _calculate_metrics(
        self,
        ticker: str,
        trades: list[BacktestTrade],
        price_history: list[dict],
        start_date: datetime,
        end_date: datetime,
    ) -> BacktestResult:
        completed_trades = [t for t in trades if t.exit_price is not None]

        total_pnl = sum(t.pnl for t in completed_trades)
        final_capital = self.initial_capital + total_pnl

        winning = [t for t in completed_trades if t.pnl > 0]
        losing = [t for t in completed_trades if t.pnl <= 0]

        win_rate = len(winning) / len(completed_trades) if completed_trades else 0
        avg_win = sum(t.pnl_pct for t in winning) / len(winning) if winning else 0
        avg_loss = sum(t.pnl_pct for t in losing) / len(losing) if losing else 0

        if price_history:
            start_price = price_history[0]["close"]
            end_price = price_history[-1]["close"]
            benchmark_return = ((end_price - start_price) / start_price) * 100
        else:
            benchmark_return = 0

        capital_history = [self.initial_capital]
        for trade in completed_trades:
            capital_history.append(capital_history[-1] + trade.pnl)

        peak = self.initial_capital
        max_dd = 0
        for cap in capital_history:
            if cap > peak:
                peak = cap
            dd = (peak - cap) / peak
            if dd > max_dd:
                max_dd = dd

        returns = []
        for i in range(1, len(capital_history)):
            ret = (capital_history[i] - capital_history[i - 1]) / capital_history[i - 1]
            returns.append(ret)

        if returns:
            avg_return = sum(returns) / len(returns)
            std_return = (
                sum((r - avg_return) ** 2 for r in returns) / len(returns)
            ) ** 0.5
            sharpe = (avg_return / std_return) * (52**0.5) if std_return > 0 else 0
        else:
            sharpe = 0

        signal_counts = {}
        for trade in trades:
            sig = trade.signal.value
            signal_counts[sig] = signal_counts.get(sig, 0) + 1

        return BacktestResult(
            ticker=ticker,
            start_date=start_date,
            end_date=end_date,
            initial_capital=self.initial_capital,
            final_capital=final_capital,
            total_return=total_pnl,
            total_return_pct=(total_pnl / self.initial_capital) * 100,
            benchmark_return_pct=benchmark_return,
            trades=completed_trades,
            winning_trades=len(winning),
            losing_trades=len(losing),
            win_rate=win_rate,
            avg_win_pct=avg_win * 100,
            avg_loss_pct=avg_loss * 100,
            max_drawdown=max_dd * 100,
            sharpe_ratio=sharpe,
            signals_generated=signal_counts,
        )

    async def compare_strategies(self, ticker: str, weeks: int = 12) -> dict:
        results = {}

        for strategy in BacktestStrategy:
            self.strategy = strategy
            result = await self.run_backtest(ticker, weeks)
            results[strategy.value] = {
                "return_pct": result["total_return_pct"],
                "win_rate": result["win_rate"],
                "sharpe": result["sharpe_ratio"],
                "max_drawdown": result["max_drawdown"],
            }

        return {
            "ticker": ticker,
            "weeks": weeks,
            "strategy_comparison": results,
            "best_strategy": max(
                results.keys(), key=lambda k: results[k]["return_pct"]
            ),
        }
