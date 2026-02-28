"""
Sector Comparison Analysis
Compare AI companies across sectors and against benchmarks
"""

import asyncio
import random
from dataclasses import dataclass
from datetime import datetime
from typing import Optional


@dataclass
class SectorMetrics:
    name: str
    avg_score: float
    avg_signal: str
    company_count: int
    top_performer: str
    bottom_performer: str
    avg_price_change_1m: float
    avg_price_change_3m: float
    concentration_score: float


@dataclass
class CompanyComparison:
    ticker: str
    company_name: str
    sector: str
    composite_score: float
    sector_rank: int
    overall_rank: int
    percentile: float
    vs_sector_avg: float
    vs_overall_avg: float
    strength: str
    weakness: str


SECTOR_MAPPING = {
    "NVDA": "Semiconductors",
    "AMD": "Semiconductors",
    "AVGO": "Semiconductors",
    "TSM": "Semiconductors",
    "MSFT": "Cloud/Software",
    "GOOGL": "Cloud/Software",
    "AMZN": "Cloud/Software",
    "ORCL": "Cloud/Software",
    "IBM": "Cloud/Software",
    "SNOW": "Cloud/Software",
    "NOW": "Cloud/Software",
    "CRM": "Cloud/Software",
    "ADBE": "Cloud/Software",
    "DDOG": "Cloud/Software",
    "META": "Social/Media",
    "AAPL": "Consumer Tech",
    "PLTR": "Enterprise AI",
    "INTU": "Fintech",
    "CRWD": "Cybersecurity",
    "AI": "Enterprise AI",
}

SECTOR_BENCHMARKS = {
    "Semiconductors": {"ticker": "SOXX", "name": "iShares Semiconductor ETF"},
    "Cloud/Software": {"ticker": "XLK", "name": "Technology Select Sector SPDR"},
    "Social/Media": {"ticker": "META", "name": "Meta Platforms"},
    "Consumer Tech": {"ticker": "XLK", "name": "Technology Select Sector SPDR"},
    "Enterprise AI": {"ticker": "BOTZ", "name": "Global X Robotics & AI ETF"},
    "Fintech": {"ticker": "ARKF", "name": "ARK Fintech Innovation ETF"},
    "Cybersecurity": {"ticker": "HACK", "name": "ETFMG Prime Cyber Security ETF"},
}


class SectorAnalyzer:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    def _get_sector(self, ticker: str) -> str:
        return SECTOR_MAPPING.get(ticker, "Other")

    def _generate_mock_price_change(self) -> tuple[float, float]:
        return (random.uniform(-15, 25), random.uniform(-30, 50))

    async def analyze_sectors(self) -> dict:
        from .config import COMPANIES
        from .watchlist import AIWatchlist

        watchlist = AIWatchlist(use_mock=True, use_cache=True)
        scores = await watchlist.analyze_all()

        sectors: dict[str, list] = {}
        for score in scores:
            sector = self._get_sector(score.ticker)
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(score)

        sector_metrics = {}
        for sector_name, sector_scores in sectors.items():
            avg_score = sum(s.composite_score for s in sector_scores) / len(
                sector_scores
            )

            sorted_scores = sorted(
                sector_scores, key=lambda s: s.composite_score, reverse=True
            )

            positive_count = sum(1 for s in sector_scores if s.composite_score > 0)
            concentration = positive_count / len(sector_scores) if sector_scores else 0

            change_1m, change_3m = self._generate_mock_price_change()

            avg_signal = self._get_avg_signal(sector_scores)

            sector_metrics[sector_name] = SectorMetrics(
                name=sector_name,
                avg_score=round(avg_score, 3),
                avg_signal=avg_signal,
                company_count=len(sector_scores),
                top_performer=sorted_scores[0].ticker if sorted_scores else None,
                bottom_performer=sorted_scores[-1].ticker if sorted_scores else None,
                avg_price_change_1m=round(change_1m, 2),
                avg_price_change_3m=round(change_3m, 2),
                concentration_score=round(concentration, 2),
            )

        all_scores_sorted = sorted(
            scores, key=lambda s: s.composite_score, reverse=True
        )
        overall_avg = (
            sum(s.composite_score for s in scores) / len(scores) if scores else 0
        )

        company_comparisons = []
        for i, score in enumerate(all_scores_sorted):
            sector = self._get_sector(score.ticker)
            sector_scores = sectors.get(sector, [])
            sector_avg = (
                sector_metrics[sector].avg_score if sector in sector_metrics else 0
            )

            sector_rank = next(
                (
                    j + 1
                    for j, s in enumerate(
                        sorted(
                            sector_scores, key=lambda x: x.composite_score, reverse=True
                        )
                    )
                    if s.ticker == score.ticker
                ),
                0,
            )

            percentile = ((len(scores) - i) / len(scores)) * 100 if scores else 0

            indicators = {s.indicator_name: s.z_score for s in score.indicator_scores}
            best_indicator = (
                max(indicators.items(), key=lambda x: x[1])[0] if indicators else "N/A"
            )
            worst_indicator = (
                min(indicators.items(), key=lambda x: x[1])[0] if indicators else "N/A"
            )

            company_comparisons.append(
                CompanyComparison(
                    ticker=score.ticker,
                    company_name=score.company_name,
                    sector=sector,
                    composite_score=round(score.composite_score, 3),
                    sector_rank=sector_rank,
                    overall_rank=i + 1,
                    percentile=round(percentile, 1),
                    vs_sector_avg=round(score.composite_score - sector_avg, 3),
                    vs_overall_avg=round(score.composite_score - overall_avg, 3),
                    strength=best_indicator.replace("_", " ").title(),
                    weakness=worst_indicator.replace("_", " ").title(),
                )
            )

        return {
            "generated_at": datetime.now().isoformat(),
            "summary": {
                "total_companies": len(scores),
                "sectors_analyzed": len(sectors),
                "bullish_sectors": len(
                    [s for s in sector_metrics.values() if s.avg_score > 0.5]
                ),
                "bearish_sectors": len(
                    [s for s in sector_metrics.values() if s.avg_score < -0.5]
                ),
            },
            "sectors": {
                name: {
                    "avg_score": m.avg_score,
                    "avg_signal": m.avg_signal,
                    "company_count": m.company_count,
                    "top_performer": m.top_performer,
                    "bottom_performer": m.bottom_performer,
                    "avg_price_change_1m": m.avg_price_change_1m,
                    "avg_price_change_3m": m.avg_price_change_3m,
                    "concentration_score": m.concentration_score,
                    "benchmark": SECTOR_BENCHMARKS.get(
                        name, {"ticker": "N/A", "name": "N/A"}
                    ),
                }
                for name, m in sector_metrics.items()
            },
            "rankings": {
                "by_sector_score": sorted(
                    sector_metrics.keys(),
                    key=lambda x: sector_metrics[x].avg_score,
                    reverse=True,
                ),
                "most_concentrated": sorted(
                    sector_metrics.keys(),
                    key=lambda x: sector_metrics[x].concentration_score,
                    reverse=True,
                )[:3],
            },
            "companies": [
                {
                    "ticker": c.ticker,
                    "name": c.company_name,
                    "sector": c.sector,
                    "score": c.composite_score,
                    "sector_rank": c.sector_rank,
                    "overall_rank": c.overall_rank,
                    "percentile": c.percentile,
                    "vs_sector_avg": c.vs_sector_avg,
                    "vs_overall_avg": c.vs_overall_avg,
                    "strength": c.strength,
                    "weakness": c.weakness,
                }
                for c in company_comparisons
            ],
            "top_picks": [
                {
                    "ticker": c.ticker,
                    "name": c.company_name,
                    "sector": c.sector,
                    "score": c.composite_score,
                    "reason": f"Strong {c.strength}, ranked #{c.sector_rank} in {c.sector}",
                }
                for c in company_comparisons[:5]
            ],
            "sector_rotation": self._generate_sector_rotation_signal(sector_metrics),
        }

    def _get_avg_signal(self, scores: list) -> str:
        if not scores:
            return "N/A"

        avg = sum(s.composite_score for s in scores) / len(scores)

        if avg >= 1.5:
            return "BUY"
        elif avg >= 0.5:
            return "LEAN BUY"
        elif avg >= -0.5:
            return "NEUTRAL"
        elif avg >= -1.5:
            return "LEAN SELL"
        else:
            return "SELL"

    def _generate_sector_rotation_signal(
        self, sector_metrics: dict[str, SectorMetrics]
    ) -> dict:
        sorted_sectors = sorted(
            sector_metrics.items(), key=lambda x: x[1].avg_score, reverse=True
        )

        if not sorted_sectors:
            return {"recommendation": "N/A", "reasoning": "Insufficient data"}

        top_sector = sorted_sectors[0]
        bottom_sector = sorted_sectors[-1]

        if top_sector[1].avg_score > 0.5:
            recommendation = f"Overweight {top_sector[0]}"
            reasoning = f"{top_sector[0]} shows strong aggregate signals ({top_sector[1].avg_score:.2f}) with {top_sector[1].company_count} companies"
        elif bottom_sector[1].avg_score < -0.5:
            recommendation = f"Underweight {bottom_sector[0]}"
            reasoning = f"{bottom_sector[0]} shows weak aggregate signals ({bottom_sector[1].avg_score:.2f})"
        else:
            recommendation = "Neutral allocation"
            reasoning = (
                "No clear sector-wide signals; focus on individual stock selection"
            )

        momentum_shifts = []
        for name, metrics in sector_metrics.items():
            if metrics.avg_price_change_1m > 10 and metrics.avg_score > 0:
                momentum_shifts.append(f"{name}: Positive momentum + bullish signals")
            elif metrics.avg_price_change_1m < -10 and metrics.avg_score < 0:
                momentum_shifts.append(f"{name}: Negative momentum + bearish signals")

        return {
            "recommendation": recommendation,
            "reasoning": reasoning,
            "top_sector": {"name": top_sector[0], "score": top_sector[1].avg_score},
            "bottom_sector": {
                "name": bottom_sector[0],
                "score": bottom_sector[1].avg_score,
            },
            "momentum_signals": momentum_shifts[:3],
            "sector_breadth": {
                "bullish": len(
                    [m for m in sector_metrics.values() if m.avg_score > 0.5]
                ),
                "neutral": len(
                    [m for m in sector_metrics.values() if -0.5 <= m.avg_score <= 0.5]
                ),
                "bearish": len(
                    [m for m in sector_metrics.values() if m.avg_score < -0.5]
                ),
            },
        }

    async def compare_companies(self, tickers: list[str]) -> dict:
        from .watchlist import AIWatchlist

        watchlist = AIWatchlist(use_mock=True, use_cache=True)

        tasks = []
        for ticker in tickers:
            from .config import COMPANIES

            company = next(
                (c for c in COMPANIES if c["ticker"] == ticker.upper()), None
            )
            if company:
                tasks.append(watchlist.analyze_company(company))

        scores = await asyncio.gather(*tasks)

        comparison = {"companies": [], "indicators": {}, "winner": None}

        indicator_totals = {}

        for score in scores:
            indicators = {s.indicator_name: s.z_score for s in score.indicator_scores}

            comparison["companies"].append(
                {
                    "ticker": score.ticker,
                    "name": score.company_name,
                    "score": round(score.composite_score, 3),
                    "signal": score.signal.value,
                    "indicators": {k: round(v, 3) for k, v in indicators.items()},
                }
            )

            for ind_name, ind_score in indicators.items():
                if ind_name not in indicator_totals:
                    indicator_totals[ind_name] = {}
                indicator_totals[ind_name][score.ticker] = ind_score

        for ind_name, scores_dict in indicator_totals.items():
            winner = max(scores_dict.items(), key=lambda x: x[1])[0]
            comparison["indicators"][ind_name] = {
                "winner": winner,
                "scores": scores_dict,
            }

        if scores:
            best = max(scores, key=lambda s: s.composite_score)
            comparison["winner"] = {
                "ticker": best.ticker,
                "score": round(best.composite_score, 3),
                "signal": best.signal.value,
            }

        return comparison
