"""
Additional Data Source Integrations
- News sentiment (via NewsAPI or similar)
- Earnings call transcripts
- Social media sentiment (Twitter/X, Reddit)
- Patent filings analysis
- Analyst ratings
"""

import asyncio
import json
import os
import random
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional
import aiohttp


@dataclass
class NewsArticle:
    title: str
    source: str
    url: str
    published_at: datetime
    sentiment: float
    ai_relevance: float


@dataclass
class EarningsData:
    ticker: str
    quarter: str
    actual_eps: float
    expected_eps: float
    surprise_pct: float
    ai_mentions_in_call: int
    ai_sentiment: float
    transcript_url: Optional[str] = None


@dataclass
class SocialSentiment:
    ticker: str
    platform: str
    mention_count: int
    sentiment_score: float
    trending: bool
    top_keywords: list[str]


@dataclass
class PatentFiling:
    title: str
    filing_date: datetime
    ai_related: bool
    category: str
    assignee: str


@dataclass
class AnalystRating:
    ticker: str
    firm: str
    analyst: str
    rating: str
    price_target: float
    date: datetime
    ai_focus: bool


class NewsIntegrator:
    def __init__(self, api_key: Optional[str] = None, use_mock: bool = True):
        self.api_key = api_key
        self.use_mock = use_mock
        self.base_url = "https://newsapi.org/v2" if api_key else None

    async def fetch_news(
        self, ticker: str, company_name: str, days: int = 7
    ) -> list[NewsArticle]:
        if self.use_mock or not self.api_key:
            return self._generate_mock_news(ticker, company_name)

        async with aiohttp.ClientSession() as session:
            params = {
                "q": f'{ticker} OR {company_name} AND (AI OR "artificial intelligence" OR "machine learning")',
                "sortBy": "publishedAt",
                "pageSize": 20,
                "from": (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d"),
                "apiKey": self.api_key,
            }
            async with session.get(
                f"{self.base_url}/everything", params=params
            ) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    return [self._parse_article(a) for a in data.get("articles", [])]
        return []

    def _generate_mock_news(self, ticker: str, company_name: str) -> list[NewsArticle]:
        headlines = [
            f"{company_name} Announces New AI Initiative",
            f"{ticker} Expands Machine Learning Capabilities",
            f"Analysts Bullish on {company_name}'s AI Strategy",
            f"{company_name} Reports Strong AI-Driven Growth",
            f"{ticker} Partners with Leading AI Research Lab",
            f"Breaking: {company_name} Unveils Next-Gen AI Platform",
            f"{ticker} CEO Discusses AI Vision in Interview",
            f"AI Revenue Boosts {company_name}'s Quarterly Results",
        ]

        return [
            NewsArticle(
                title=random.choice(headlines),
                source=random.choice(
                    ["Bloomberg", "Reuters", "TechCrunch", "WSJ", "CNBC"]
                ),
                url=f"https://example.com/news/{ticker}/{i}",
                published_at=datetime.now()
                - timedelta(days=random.randint(0, 7), hours=random.randint(0, 23)),
                sentiment=random.uniform(-0.5, 0.8),
                ai_relevance=random.uniform(0.3, 1.0),
            )
            for i in range(random.randint(5, 15))
        ]

    def _parse_article(self, data: dict) -> NewsArticle:
        return NewsArticle(
            title=data.get("title", ""),
            source=data.get("source", {}).get("name", "Unknown"),
            url=data.get("url", ""),
            published_at=datetime.fromisoformat(
                data.get("publishedAt", "").replace("Z", "+00:00")
            ),
            sentiment=random.uniform(-0.3, 0.6),
            ai_relevance=random.uniform(0.2, 1.0),
        )

    def calculate_sentiment_score(self, articles: list[NewsArticle]) -> float:
        if not articles:
            return 0.0

        weighted = sum(a.sentiment * a.ai_relevance for a in articles)
        total_weight = sum(a.ai_relevance for a in articles)

        return weighted / total_weight if total_weight > 0 else 0.0


class EarningsIntegrator:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    async def fetch_earnings(self, ticker: str) -> Optional[EarningsData]:
        if self.use_mock:
            return self._generate_mock_earnings(ticker)
        return None

    def _generate_mock_earnings(self, ticker: str) -> EarningsData:
        actual = random.uniform(0.5, 5.0)
        expected = actual * random.uniform(0.9, 1.1)

        return EarningsData(
            ticker=ticker,
            quarter=f"Q{random.randint(1, 4)} 202{random.randint(4, 6)}",
            actual_eps=actual,
            expected_eps=expected,
            surprise_pct=((actual - expected) / expected) * 100,
            ai_mentions_in_call=random.randint(5, 50),
            ai_sentiment=random.uniform(-0.3, 0.7),
        )


class SocialSentimentIntegrator:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    async def fetch_sentiment(self, ticker: str) -> list[SocialSentiment]:
        if self.use_mock:
            return self._generate_mock_sentiment(ticker)
        return []

    def _generate_mock_sentiment(self, ticker: str) -> list[SocialSentiment]:
        platforms = ["Twitter/X", "Reddit", "StockTwits"]

        return [
            SocialSentiment(
                ticker=ticker,
                platform=platform,
                mention_count=random.randint(100, 10000),
                sentiment_score=random.uniform(-0.5, 0.8),
                trending=random.choice([True, False, False]),
                top_keywords=random.sample(
                    [
                        "AI",
                        "bullish",
                        "earnings",
                        "growth",
                        "buy",
                        "hold",
                        "sell",
                        "upgrade",
                    ],
                    4,
                ),
            )
            for platform in platforms
        ]

    def calculate_aggregate_sentiment(self, sentiments: list[SocialSentiment]) -> float:
        if not sentiments:
            return 0.0

        weighted = sum(s.sentiment_score * (s.mention_count / 1000) for s in sentiments)
        total_weight = sum(s.mention_count / 1000 for s in sentiments)

        return weighted / total_weight if total_weight > 0 else 0.0


class PatentIntegrator:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    async def fetch_patents(
        self, company_name: str, weeks: int = 4
    ) -> list[PatentFiling]:
        if self.use_mock:
            return self._generate_mock_patents(company_name)
        return []

    def _generate_mock_patents(self, company_name: str) -> list[PatentFiling]:
        categories = [
            "Neural Network Architecture",
            "Natural Language Processing",
            "Computer Vision",
            "Autonomous Systems",
            "AI Chip Design",
            "Machine Learning Methods",
            "Data Processing",
            "Speech Recognition",
        ]

        return [
            PatentFiling(
                title=f"{random.choice(categories)} System and Method",
                filing_date=datetime.now() - timedelta(days=random.randint(0, 28)),
                ai_related=True,
                category=random.choice(categories),
                assignee=company_name,
            )
            for _ in range(random.randint(2, 8))
        ]

    def calculate_innovation_score(self, patents: list[PatentFiling]) -> float:
        ai_patents = [p for p in patents if p.ai_related]
        return min(len(ai_patents) / 5, 2.0)


class AnalystIntegrator:
    def __init__(self, use_mock: bool = True):
        self.use_mock = use_mock

    async def fetch_ratings(self, ticker: str) -> list[AnalystRating]:
        if self.use_mock:
            return self._generate_mock_ratings(ticker)
        return []

    def _generate_mock_ratings(self, ticker: str) -> list[AnalystRating]:
        firms = [
            "Goldman Sachs",
            "Morgan Stanley",
            "JPMorgan",
            "Bank of America",
            "Citigroup",
            "UBS",
            "Deutsche Bank",
        ]
        ratings = ["Strong Buy", "Buy", "Hold", "Underweight", "Sell"]
        weights = [0.15, 0.35, 0.30, 0.15, 0.05]

        return [
            AnalystRating(
                ticker=ticker,
                firm=random.choice(firms),
                analyst=f"Analyst {random.randint(1, 50)}",
                rating=random.choices(ratings, weights)[0],
                price_target=random.uniform(50, 1000),
                date=datetime.now() - timedelta(days=random.randint(0, 90)),
                ai_focus=random.choice([True, False]),
            )
            for _ in range(random.randint(3, 10))
        ]

    def calculate_consensus(self, ratings: list[AnalystRating]) -> dict:
        if not ratings:
            return {"consensus": "N/A", "avg_target": 0, "buy_ratio": 0}

        rating_scores = {
            "Strong Buy": 5,
            "Buy": 4,
            "Hold": 3,
            "Underweight": 2,
            "Sell": 1,
        }
        avg_score = sum(rating_scores.get(r.rating, 3) for r in ratings) / len(ratings)

        buy_count = len([r for r in ratings if r.rating in ["Strong Buy", "Buy"]])

        if avg_score >= 4:
            consensus = "Buy"
        elif avg_score >= 3:
            consensus = "Hold"
        else:
            consensus = "Sell"

        return {
            "consensus": consensus,
            "avg_score": round(avg_score, 2),
            "avg_target": round(sum(r.price_target for r in ratings) / len(ratings), 2),
            "buy_ratio": round(buy_count / len(ratings), 2),
        }


class DataIntegrator:
    def __init__(self, use_mock: bool = True, news_api_key: Optional[str] = None):
        self.news = NewsIntegrator(api_key=news_api_key, use_mock=use_mock)
        self.earnings = EarningsIntegrator(use_mock=use_mock)
        self.social = SocialSentimentIntegrator(use_mock=use_mock)
        self.patents = PatentIntegrator(use_mock=use_mock)
        self.analysts = AnalystIntegrator(use_mock=use_mock)

    async def fetch_all(self, ticker: str, company_name: str) -> dict:
        results = await asyncio.gather(
            self.news.fetch_news(ticker, company_name),
            self.earnings.fetch_earnings(ticker),
            self.social.fetch_sentiment(ticker),
            self.patents.fetch_patents(company_name),
            self.analysts.fetch_ratings(ticker),
            return_exceptions=True,
        )

        news_articles = results[0] if not isinstance(results[0], Exception) else []
        earnings_data = results[1] if not isinstance(results[1], Exception) else None
        social_sentiment = results[2] if not isinstance(results[2], Exception) else []
        patent_filings = results[3] if not isinstance(results[3], Exception) else []
        analyst_ratings = results[4] if not isinstance(results[4], Exception) else []

        return {
            "ticker": ticker,
            "company_name": company_name,
            "news": {
                "articles": [
                    {
                        "title": a.title,
                        "source": a.source,
                        "sentiment": round(a.sentiment, 2),
                    }
                    for a in news_articles[:10]
                ],
                "sentiment_score": round(
                    self.news.calculate_sentiment_score(news_articles), 3
                ),
                "article_count": len(news_articles),
            },
            "earnings": {
                "quarter": earnings_data.quarter if earnings_data else None,
                "surprise_pct": round(earnings_data.surprise_pct, 2)
                if earnings_data
                else None,
                "ai_mentions": earnings_data.ai_mentions_in_call
                if earnings_data
                else 0,
                "ai_sentiment": round(earnings_data.ai_sentiment, 2)
                if earnings_data
                else None,
            },
            "social": {
                "platforms": [
                    {
                        "name": s.platform,
                        "mentions": s.mention_count,
                        "sentiment": round(s.sentiment_score, 2),
                    }
                    for s in social_sentiment
                ],
                "aggregate_sentiment": round(
                    self.social.calculate_aggregate_sentiment(social_sentiment), 3
                ),
            },
            "patents": {
                "filings_count": len(patent_filings),
                "ai_patents": len([p for p in patent_filings if p.ai_related]),
                "innovation_score": round(
                    self.patents.calculate_innovation_score(patent_filings), 2
                ),
            },
            "analysts": {
                "ratings": [
                    {
                        "firm": r.firm,
                        "rating": r.rating,
                        "target": round(r.price_target, 2),
                    }
                    for r in analyst_ratings
                ],
                **self.analysts.calculate_consensus(analyst_ratings),
            },
        }
