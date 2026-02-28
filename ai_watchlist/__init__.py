"""
AI Watchlist - Track leading indicators for AI companies
"""

from .watchlist import AIWatchlist
from .models import CompanyScore, SignalType, IndicatorScore
from .config import COMPANIES, INDICATOR_WEIGHTS
from .scoring import ScoringEngine
from .alerts import AlertManager, AlertConfig, Alert, AlertType
from .backtest import Backtester, BacktestStrategy, BacktestResult
from .sectors import SectorAnalyzer

__version__ = "2.0.0"
__all__ = [
    "AIWatchlist",
    "CompanyScore",
    "SignalType",
    "IndicatorScore",
    "COMPANIES",
    "INDICATOR_WEIGHTS",
    "ScoringEngine",
    "AlertManager",
    "AlertConfig",
    "Alert",
    "AlertType",
    "Backtester",
    "BacktestStrategy",
    "BacktestResult",
    "SectorAnalyzer",
]
