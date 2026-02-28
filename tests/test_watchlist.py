"""
Tests for AI Watchlist
"""

import pytest
from ai_watchlist.config import COMPANIES, INDICATOR_WEIGHTS, SIGNAL_THRESHOLDS
from ai_watchlist.models import SignalType
from ai_watchlist.scoring import ScoringEngine


class TestConfig:
    def test_companies_count(self):
        assert len(COMPANIES) == 20

    def test_companies_have_required_fields(self):
        required = ["ticker", "name", "sec_cik", "github_orgs"]
        for company in COMPANIES:
            for field in required:
                assert field in company

    def test_weights_sum_to_one(self):
        total = sum(INDICATOR_WEIGHTS.values())
        assert abs(total - 1.0) < 0.001

    def test_thresholds_defined(self):
        required = [
            "strong_buy",
            "buy",
            "neutral_upper",
            "neutral_lower",
            "sell",
            "strong_sell",
        ]
        for threshold in required:
            assert threshold in SIGNAL_THRESHOLDS


class TestModels:
    def test_signal_type_values(self):
        assert SignalType.STRONG_BUY.value == "STRONG BUY"
        assert SignalType.BUY.value == "BUY"
        assert SignalType.HOLD.value == "HOLD"
        assert SignalType.SELL.value == "SELL"
        assert SignalType.STRONG_SELL.value == "STRONG SELL"


class TestScoringEngine:
    def test_determine_signal_strong_buy(self):
        engine = ScoringEngine()
        signal = engine.determine_signal(2.5, consecutive_weeks=2)
        assert signal == SignalType.STRONG_BUY

    def test_determine_signal_buy(self):
        engine = ScoringEngine()
        signal = engine.determine_signal(1.5, consecutive_weeks=1)
        assert signal == SignalType.BUY

    def test_determine_signal_hold(self):
        engine = ScoringEngine()
        signal = engine.determine_signal(0.5, consecutive_weeks=1)
        assert signal == SignalType.HOLD

    def test_determine_signal_sell(self):
        engine = ScoringEngine()
        signal = engine.determine_signal(-1.5, consecutive_weeks=1)
        assert signal == SignalType.SELL

    def test_determine_signal_strong_sell(self):
        engine = ScoringEngine()
        signal = engine.determine_signal(-2.5, consecutive_weeks=2)
        assert signal == SignalType.STRONG_SELL

    def test_calculate_z_score_no_history(self):
        engine = ScoringEngine()
        z = engine.calculate_z_score(1.0, "TEST", "test_indicator")
        assert z == 0.0

    def test_rolling_stats_no_history(self):
        engine = ScoringEngine()
        mean, std = engine.get_rolling_stats("TEST", "test_indicator")
        assert mean == 0.0
        assert std == 1.0


class TestIndicators:
    @pytest.mark.asyncio
    async def test_sec_indicator(self):
        from ai_watchlist.indicators import SECFilingsIndicator

        indicator = SECFilingsIndicator(use_cache=False)
        result = await indicator.get_indicator_value("TEST", "0000000000")
        assert "value" in result
        assert "details" in result

    @pytest.mark.asyncio
    async def test_jobs_indicator(self):
        from ai_watchlist.indicators import JobPostingsIndicator

        indicator = JobPostingsIndicator(use_mock=True, use_cache=False)
        result = await indicator.get_indicator_value("Test Company", "TEST")
        assert "value" in result
        assert "details" in result

    @pytest.mark.asyncio
    async def test_github_indicator(self):
        from ai_watchlist.indicators import GitHubIndicator

        indicator = GitHubIndicator(use_mock=True, use_cache=False)
        result = await indicator.get_indicator_value(["test-org"], "TEST")
        assert "value" in result
        assert "details" in result

    @pytest.mark.asyncio
    async def test_exec_indicator(self):
        from ai_watchlist.indicators import ExecutiveIndicator

        indicator = ExecutiveIndicator(use_mock=True, use_cache=False)
        result = await indicator.get_indicator_value("Test Company", "TEST")
        assert "value" in result
        assert "details" in result

    @pytest.mark.asyncio
    async def test_sentiment_indicator(self):
        from ai_watchlist.indicators import EmployeeSentimentIndicator

        indicator = EmployeeSentimentIndicator(use_mock=True, use_cache=False)
        result = await indicator.get_indicator_value("Test Company", "TEST")
        assert "value" in result
        assert "details" in result

    @pytest.mark.asyncio
    async def test_govt_indicator(self):
        from ai_watchlist.indicators import GovernmentContractsIndicator

        indicator = GovernmentContractsIndicator(use_mock=True, use_cache=False)
        result = await indicator.get_indicator_value("Test Company", "TEST")
        assert "value" in result
        assert "details" in result
