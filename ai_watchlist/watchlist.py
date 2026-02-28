"""
AI Watchlist - Main watchlist manager
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional
import aiohttp

from .config import COMPANIES, INDICATOR_WEIGHTS
from .models import CompanyScore, SignalType
from .indicators import (
    SECFilingsIndicator,
    JobPostingsIndicator,
    GitHubIndicator,
    ExecutiveIndicator,
    EmployeeSentimentIndicator,
    GovernmentContractsIndicator,
)
from .scoring import ScoringEngine

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")


class AIWatchlist:
    def __init__(
        self,
        use_mock: bool = True,
        use_cache: bool = True,
        github_token: Optional[str] = None,
    ):
        self.use_mock = use_mock
        self.use_cache = use_cache

        self.sec_indicator = SECFilingsIndicator(use_cache=use_cache)
        self.jobs_indicator = JobPostingsIndicator(
            use_mock=use_mock, use_cache=use_cache
        )
        self.github_indicator = GitHubIndicator(
            github_token=github_token, use_cache=use_cache, use_mock=use_mock
        )
        self.exec_indicator = ExecutiveIndicator(use_mock=use_mock, use_cache=use_cache)
        self.sentiment_indicator = EmployeeSentimentIndicator(
            use_mock=use_mock, use_cache=use_cache
        )
        self.govt_indicator = GovernmentContractsIndicator(
            use_mock=use_mock, use_cache=use_cache
        )

        self.scoring_engine = ScoringEngine()

        os.makedirs(DATA_DIR, exist_ok=True)

    async def analyze_company(self, company: dict) -> CompanyScore:
        ticker = company["ticker"]
        company_name = company["name"]
        cik = company.get("sec_cik", "")
        github_orgs = company.get("github_orgs", [])

        tasks = [
            self.sec_indicator.get_indicator_value(ticker, cik),
            self.jobs_indicator.get_indicator_value(company_name, ticker),
            self.github_indicator.get_indicator_value(github_orgs, ticker),
            self.exec_indicator.get_indicator_value(company_name, ticker),
            self.sentiment_indicator.get_indicator_value(company_name, ticker),
            self.govt_indicator.get_indicator_value(company_name, ticker),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        indicator_values = {}
        details = {}

        indicator_names = list(INDICATOR_WEIGHTS.keys())

        for i, result in enumerate(results):
            ind_name = indicator_names[i]
            if isinstance(result, Exception):
                print(f"Error for {ticker} - {ind_name}: {result}")
                indicator_values[ind_name] = 0.0
                details[ind_name] = {"error": str(result)}
            else:
                indicator_values[ind_name] = result["value"]
                details[ind_name] = result.get("details", {})

        score = self.scoring_engine.calculate_composite_score(ticker, indicator_values)
        score.company_name = company_name

        for s in score.indicator_scores:
            if s.indicator_name in details:
                s.details = details[s.indicator_name]

        return score

    async def analyze_all(
        self, tickers: Optional[list[str]] = None
    ) -> list[CompanyScore]:
        companies = COMPANIES
        if tickers:
            companies = [c for c in COMPANIES if c["ticker"] in tickers]

        tasks = [self.analyze_company(c) for c in companies]
        scores = await asyncio.gather(*tasks)

        return sorted(scores, key=lambda s: s.composite_score, reverse=True)

    def save_results(self, scores: list[CompanyScore], filename: str = None):
        if not filename:
            filename = f"watchlist_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        path = os.path.join(DATA_DIR, filename)

        data = {
            "generated_at": datetime.now().isoformat(),
            "total_companies": len(scores),
            "summary": {
                "strong_buy": len(
                    [s for s in scores if s.signal == SignalType.STRONG_BUY]
                ),
                "buy": len([s for s in scores if s.signal == SignalType.BUY]),
                "hold": len([s for s in scores if s.signal == SignalType.HOLD]),
                "sell": len([s for s in scores if s.signal == SignalType.SELL]),
                "strong_sell": len(
                    [s for s in scores if s.signal == SignalType.STRONG_SELL]
                ),
            },
            "rankings": [
                {"rank": i + 1, **score.to_dict()} for i, score in enumerate(scores)
            ],
        }

        with open(path, "w") as f:
            json.dump(data, f, indent=2)

        return path

    def load_results(self, filename: str) -> dict:
        path = os.path.join(DATA_DIR, filename)
        with open(path, "r") as f:
            return json.load(f)

    def get_company_history(self, ticker: str) -> dict:
        return self.scoring_engine.load_history(ticker)

    def print_report(self, scores: list[CompanyScore], top_n: int = 20):
        print("\n" + "=" * 80)
        print("AI COMPANY WATCHLIST - WEEKLY SIGNALS REPORT")
        print(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 80)

        print("\nSIGNAL SUMMARY:")
        print("-" * 40)
        signals = {}
        for s in scores:
            signals[s.signal.value] = signals.get(s.signal.value, 0) + 1

        for signal, count in sorted(signals.items()):
            print(f"  {signal:15} : {count:3} companies")

        print("\n" + "=" * 80)
        print(f"TOP {top_n} RANKINGS (by composite score)")
        print("=" * 80)

        header = f"{'Rank':>4} {'Ticker':>6} {'Score':>8} {'Signal':>14} {'SEC':>6} {'Jobs':>6} {'GitHub':>6} {'Exec':>6} {'Sent':>6} {'Govt':>6}"
        print(header)
        print("-" * 80)

        for i, score in enumerate(scores[:top_n]):
            indicators = {s.indicator_name: s.z_score for s in score.indicator_scores}

            row = (
                f"{i + 1:>4} "
                f"{score.ticker:>6} "
                f"{score.composite_score:>8.3f} "
                f"{score.signal.value:>14} "
                f"{indicators.get('sec_filings', 0):>6.2f} "
                f"{indicators.get('job_postings', 0):>6.2f} "
                f"{indicators.get('github_activity', 0):>6.2f} "
                f"{indicators.get('exec_appearances', 0):>6.2f} "
                f"{indicators.get('employee_sentiment', 0):>6.2f} "
                f"{indicators.get('govt_contracts', 0):>6.2f}"
            )
            print(row)

        print("\n" + "=" * 80)
        print("LEGEND:")
        print("  Score: Composite Z-score (higher = more bullish)")
        print("  Columns show Z-scores for each indicator")
        print(
            "  Signal thresholds: >2.0=STRONG BUY, >1.0=BUY, <-1.0=SELL, <-2.0=STRONG SELL"
        )
        print("=" * 80 + "\n")

    def print_company_detail(self, score: CompanyScore):
        print("\n" + "=" * 60)
        print(f"{score.company_name} ({score.ticker})")
        print("=" * 60)
        print(f"Composite Score: {score.composite_score:.3f}")
        print(f"Signal: {score.signal.value}")
        print("\nIndicator Breakdown:")
        print("-" * 60)

        for s in score.indicator_scores:
            print(f"\n{s.indicator_name.upper()} (weight: {s.weight:.0%})")
            print(f"  Raw Value:  {s.raw_value:.3f}")
            print(f"  Z-Score:    {s.z_score:.3f}")
            if s.details:
                print(f"  Details:    {s.details}")

        print("=" * 60 + "\n")
