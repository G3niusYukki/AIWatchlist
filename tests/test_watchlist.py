"""
Tests for AI Watchlist v2.0
"""

import pytest
from ai_watchlist.config import COMPANIES, INDICATOR_WEIGHTS, SIGNAL_THRESHOLDS
from ai_watchlist.models import SignalType
from ai_watchlist.scoring import ScoringEngine
from ai_watchlist.alerts import AlertConfig, AlertType


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


class TestAlerts:
    def test_alert_config_defaults(self):
        config = AlertConfig()
        assert config.email_enabled == False
        assert config.slack_enabled == False
        assert config.alert_on_signal_change == True

    def test_alert_types(self):
        assert AlertType.SIGNAL_UPGRADE.value == "SIGNAL_UPGRADE"
        assert AlertType.SIGNAL_DOWNGRADE.value == "SIGNAL_DOWNGRADE"
        assert AlertType.STRONG_BUY.value == "STRONG_BUY"
        assert AlertType.STRONG_SELL.value == "STRONG_SELL"


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


class TestPriceIntegration:
    @pytest.mark.asyncio
    async def test_price_integrator(self):
        from ai_watchlist.indicators import PriceIntegrator

        integrator = PriceIntegrator(use_cache=False)
        price = await integrator.fetch_price("TEST")
        assert hasattr(price, "ticker")
        assert hasattr(price, "current_price")
        assert hasattr(price, "fifty_day_ma")

    @pytest.mark.asyncio
    async def test_price_momentum_score(self):
        from ai_watchlist.indicators import PriceIntegrator, PriceData
        from datetime import datetime

        integrator = PriceIntegrator()
        price = PriceData(
            ticker="TEST",
            current_price=100,
            previous_close=95,
            day_change=5,
            day_change_pct=5.26,
            week_change_pct=10,
            month_change_pct=20,
            volume=1000000,
            avg_volume=800000,
            market_cap=1e9,
            pe_ratio=25,
            fifty_day_ma=90,
            two_hundred_day_ma=80,
            fifty_two_week_high=110,
            fifty_two_week_low=50,
            above_50dma=True,
            above_200dma=True,
            timestamp=datetime.now(),
        )
        score = integrator.calculate_price_momentum_score(price)
        assert isinstance(score, float)


class TestDataSources:
    @pytest.mark.asyncio
    async def test_news_integrator(self):
        from ai_watchlist.indicators import NewsIntegrator

        integrator = NewsIntegrator(use_mock=True)
        articles = await integrator.fetch_news("TEST", "Test Company")
        assert isinstance(articles, list)

    @pytest.mark.asyncio
    async def test_earnings_integrator(self):
        from ai_watchlist.indicators import EarningsIntegrator

        integrator = EarningsIntegrator(use_mock=True)
        earnings = await integrator.fetch_earnings("TEST")
        assert earnings is not None

    @pytest.mark.asyncio
    async def test_social_sentiment_integrator(self):
        from ai_watchlist.indicators import SocialSentimentIntegrator

        integrator = SocialSentimentIntegrator(use_mock=True)
        sentiment = await integrator.fetch_sentiment("TEST")
        assert isinstance(sentiment, list)

    @pytest.mark.asyncio
    async def test_patent_integrator(self):
        from ai_watchlist.indicators import PatentIntegrator

        integrator = PatentIntegrator(use_mock=True)
        patents = await integrator.fetch_patents("Test Company")
        assert isinstance(patents, list)

    @pytest.mark.asyncio
    async def test_analyst_integrator(self):
        from ai_watchlist.indicators import AnalystIntegrator

        integrator = AnalystIntegrator(use_mock=True)
        ratings = await integrator.fetch_ratings("TEST")
        assert isinstance(ratings, list)

    @pytest.mark.asyncio
    async def test_data_integrator(self):
        from ai_watchlist.indicators import DataIntegrator

        integrator = DataIntegrator(use_mock=True)
        data = await integrator.fetch_all("TEST", "Test Company")
        assert "news" in data
        assert "earnings" in data
        assert "social" in data
        assert "patents" in data
        assert "analysts" in data


class TestBacktest:
    @pytest.mark.asyncio
    async def test_backtester(self):
        from ai_watchlist.backtest import Backtester

        backtester = Backtester(initial_capital=100000)
        result = await backtester.run_backtest("TEST", weeks=4)
        assert "ticker" in result
        assert "total_return_pct" in result
        assert "sharpe_ratio" in result

    @pytest.mark.asyncio
    async def test_strategy_comparison(self):
        from ai_watchlist.backtest import Backtester

        backtester = Backtester()
        result = await backtester.compare_strategies("TEST", weeks=4)
        assert "strategy_comparison" in result
        assert "best_strategy" in result


class TestSectors:
    @pytest.mark.asyncio
    async def test_sector_analyzer(self):
        from ai_watchlist.sectors import SectorAnalyzer

        analyzer = SectorAnalyzer(use_mock=True)
        result = await analyzer.analyze_sectors()
        assert "sectors" in result
        assert "companies" in result
        assert "sector_rotation" in result

    @pytest.mark.asyncio
    async def test_company_comparison(self):
        from ai_watchlist.sectors import SectorAnalyzer

        analyzer = SectorAnalyzer(use_mock=True)
        result = await analyzer.compare_companies(["NVDA", "AMD"])
        assert "companies" in result
        assert "winner" in result
