"""
Scoring and Signal Generation
Calculates composite scores and generates buy/sell signals
"""

import json
import os
from datetime import datetime
from typing import Optional
from collections import defaultdict

from .config import INDICATOR_WEIGHTS, SIGNAL_THRESHOLDS, ROLLING_WEEKS
from .models import IndicatorScore, CompanyScore, SignalType, HistoricalData

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class ScoringEngine:
    def __init__(self, historical_dir: str = None):
        self.historical_dir = historical_dir or os.path.join(DATA_DIR, "historical")
        self.history: dict[str, dict[str, list]] = defaultdict(
            lambda: defaultdict(list)
        )
        os.makedirs(self.historical_dir, exist_ok=True)

    def _get_history_path(self, ticker: str) -> str:
        return os.path.join(self.historical_dir, f"{ticker}_history.json")

    def load_history(self, ticker: str) -> dict:
        path = self._get_history_path(ticker)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return {}

    def save_history(self, ticker: str, history: dict):
        path = self._get_history_path(ticker)
        with open(path, "w") as f:
            json.dump(history, f, indent=2)

    def record_score(
        self, ticker: str, indicator_name: str, value: float, timestamp: str = None
    ):
        history = self.load_history(ticker)
        if indicator_name not in history:
            history[indicator_name] = []

        entry = {"value": value, "timestamp": timestamp or datetime.now().isoformat()}
        history[indicator_name].append(entry)

        history[indicator_name] = history[indicator_name][-ROLLING_WEEKS * 4 :]

        self.save_history(ticker, history)

    def get_rolling_stats(
        self, ticker: str, indicator_name: str
    ) -> tuple[float, float]:
        history = self.load_history(ticker)
        values = [e["value"] for e in history.get(indicator_name, [])]

        if len(values) < 2:
            return 0.0, 1.0

        mean = sum(values) / len(values)
        variance = sum((x - mean) ** 2 for x in values) / len(values)
        std = variance**0.5

        return mean, std if std > 0 else 1.0

    def calculate_z_score(
        self, current_value: float, ticker: str, indicator_name: str
    ) -> float:
        mean, std = self.get_rolling_stats(ticker, indicator_name)

        if std == 0:
            return 0.0

        z_score = (current_value - mean) / std
        return max(-3.0, min(3.0, z_score))

    def determine_signal(
        self, composite_score: float, consecutive_weeks: int = 1
    ) -> SignalType:
        if (
            composite_score >= SIGNAL_THRESHOLDS["strong_buy"]
            and consecutive_weeks >= 2
        ):
            return SignalType.STRONG_BUY
        elif composite_score >= SIGNAL_THRESHOLDS["buy"]:
            return SignalType.BUY
        elif (
            composite_score <= SIGNAL_THRESHOLDS["strong_sell"]
            and consecutive_weeks >= 2
        ):
            return SignalType.STRONG_SELL
        elif composite_score <= SIGNAL_THRESHOLDS["sell"]:
            return SignalType.SELL
        else:
            return SignalType.HOLD

    def calculate_composite_score(
        self, ticker: str, indicator_values: dict[str, float], record: bool = True
    ) -> CompanyScore:
        indicator_scores: list[IndicatorScore] = []
        weighted_sum = 0.0
        total_weight = 0.0

        for indicator_name, weight in INDICATOR_WEIGHTS.items():
            if indicator_name not in indicator_values:
                continue

            raw_value = indicator_values[indicator_name]
            z_score = self.calculate_z_score(raw_value, ticker, indicator_name)

            if record:
                self.record_score(ticker, indicator_name, raw_value)

            score = IndicatorScore(
                indicator_name=indicator_name,
                raw_value=raw_value,
                z_score=z_score,
                weight=weight,
            )
            indicator_scores.append(score)

            weighted_sum += z_score * weight
            total_weight += weight

        composite = weighted_sum / total_weight if total_weight > 0 else 0.0

        signal = self.determine_signal(composite)

        return CompanyScore(
            ticker=ticker,
            company_name="",
            composite_score=composite,
            signal=signal,
            indicator_scores=indicator_scores,
        )

    def get_weekly_report(self, ticker: str) -> dict:
        history = self.load_history(ticker)

        report = {"ticker": ticker, "indicators": {}, "trends": {}}

        for indicator_name, entries in history.items():
            if not entries:
                continue

            recent = entries[-4:] if len(entries) >= 4 else entries
            values = [e["value"] for e in recent]

            mean = sum(values) / len(values)
            current = values[-1] if values else 0
            trend = (
                "up"
                if len(values) >= 2 and values[-1] > values[-2]
                else "down"
                if len(values) >= 2
                else "flat"
            )

            report["indicators"][indicator_name] = {
                "current": round(current, 3),
                "4wk_avg": round(mean, 3),
                "trend": trend,
            }

        return report
