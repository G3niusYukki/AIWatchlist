"""
AI Watchlist - Track leading indicators for AI companies
"""

from .watchlist import AIWatchlist
from .models import CompanyScore, SignalType, IndicatorScore
from .config import COMPANIES, INDICATOR_WEIGHTS
from .scoring import ScoringEngine

__version__ = "1.0.0"
__all__ = [
    "AIWatchlist",
    "CompanyScore",
    "SignalType",
    "IndicatorScore",
    "COMPANIES",
    "INDICATOR_WEIGHTS",
    "ScoringEngine",
]
