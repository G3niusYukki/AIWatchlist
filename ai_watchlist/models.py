"""
Data models for AI Watchlist
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
from enum import Enum


class SignalType(Enum):
    STRONG_BUY = "STRONG BUY"
    BUY = "BUY"
    HOLD = "HOLD"
    SELL = "SELL"
    STRONG_SELL = "STRONG SELL"


@dataclass
class IndicatorScore:
    indicator_name: str
    raw_value: float
    z_score: float
    weight: float
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict = field(default_factory=dict)


@dataclass
class CompanyScore:
    ticker: str
    company_name: str
    composite_score: float
    signal: SignalType
    indicator_scores: list[IndicatorScore] = field(default_factory=list)
    price_context: Optional[dict] = None
    sector_context: Optional[dict] = None
    timestamp: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "composite_score": round(self.composite_score, 3),
            "signal": self.signal.value,
            "indicators": {
                s.indicator_name: {
                    "z_score": round(s.z_score, 3),
                    "raw_value": round(s.raw_value, 3),
                    "weight": s.weight,
                    "details": s.details,
                }
                for s in self.indicator_scores
            },
            "timestamp": self.timestamp.isoformat(),
        }


@dataclass
class HistoricalData:
    ticker: str
    indicator_name: str
    values: list[float]
    dates: list[str]

    def get_rolling_stats(self) -> tuple[float, float]:
        if len(self.values) < 2:
            return 0.0, 1.0
        mean = sum(self.values) / len(self.values)
        variance = sum((x - mean) ** 2 for x in self.values) / len(self.values)
        std = variance**0.5
        return mean, std if std > 0 else 1.0
