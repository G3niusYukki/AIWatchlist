"""
Executive Appearances Indicator
Tracks public statements, conference appearances, and AI mentions
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

EXECUTIVE_SOURCES = [
    "earnings_calls",
    "conference_keynotes",
    "podcast_appearances",
    "twitter_x",
    "press_releases",
    "interviews",
]

POSITIVE_KEYWORDS = [
    "breakthrough",
    "accelerating",
    "exceed expectations",
    "strong demand",
    "significant growth",
    "market leader",
    "innovative",
    "ahead of schedule",
    "expanding",
    "record",
    "best-in-class",
]

NEGATIVE_KEYWORDS = [
    "challenging",
    "headwinds",
    "cautious",
    "uncertain",
    "competitive pressure",
    "slowing",
    "delay",
    "below expectations",
    "restructuring",
    "difficult",
]

AI_MENTIONS_KEYWORDS = [
    "AI",
    "artificial intelligence",
    "machine learning",
    "LLM",
    "GPT",
    "generative AI",
    "deep learning",
    "neural network",
    "transformer",
]


class ExecutiveIndicator:
    def __init__(self, use_mock: bool = True, use_cache: bool = True):
        self.use_mock = use_mock
        self.use_cache = use_cache

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(DATA_DIR, f"exec_{ticker}.json")

    def _generate_mock_data(self, company_name: str) -> dict:
        ai_mentions = random.randint(5, 50)
        total_statements = random.randint(20, 100)

        positive_count = random.randint(3, ai_mentions)
        negative_count = random.randint(0, ai_mentions // 3)

        return {
            "ai_mentions": ai_mentions,
            "total_statements": total_statements,
            "ai_mention_ratio": ai_mentions / total_statements
            if total_statements > 0
            else 0,
            "positive_keywords": positive_count,
            "negative_keywords": negative_count,
            "sentiment_score": (positive_count - negative_count) / ai_mentions
            if ai_mentions > 0
            else 0,
            "recent_appearances": [
                {
                    "type": random.choice(EXECUTIVE_SOURCES),
                    "date": (
                        datetime.now() - timedelta(days=random.randint(1, 28))
                    ).strftime("%Y-%m-%d"),
                    "ai_mentions": random.randint(1, 10),
                    "sentiment": random.choice(
                        ["positive", "neutral", "positive", "positive"]
                    ),
                }
                for _ in range(random.randint(3, 8))
            ],
            "new_product_announcements": random.randint(0, 3),
            "partnership_announcements": random.randint(0, 2),
        }

    async def fetch_appearances(self, company_name: str, ticker: str) -> dict:
        path = self._get_cache_path(ticker)

        if self.use_cache and os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(
                    data.get("timestamp", "2000-01-01")
                )
                if datetime.now() - cached_time < timedelta(hours=24):
                    return data

        if self.use_mock:
            data = self._generate_mock_data(company_name)
        else:
            data = await self._fetch_real_data(company_name)

        data["timestamp"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

        return data

    async def _fetch_real_data(self, company_name: str) -> dict:
        return self._generate_mock_data(company_name)

    def calculate_score(self, exec_data: dict) -> float:
        sentiment = exec_data.get("sentiment_score", 0)
        ai_ratio = exec_data.get("ai_mention_ratio", 0)
        new_products = exec_data.get("new_product_announcements", 0)
        partnerships = exec_data.get("partnership_announcements", 0)

        score = 0.0
        score += sentiment * 1.5
        score += min(ai_ratio * 5, 1.0)
        score += min(new_products * 0.3, 0.6)
        score += min(partnerships * 0.2, 0.4)

        return max(-2.0, min(2.0, score))

    async def get_indicator_value(self, company_name: str, ticker: str) -> dict:
        data = await self.fetch_appearances(company_name, ticker)
        score = self.calculate_score(data)
        return {
            "value": score,
            "details": {
                "ai_mentions": data.get("ai_mentions", 0),
                "sentiment_score": round(data.get("sentiment_score", 0), 2),
                "new_products": data.get("new_product_announcements", 0),
                "partnerships": data.get("partnership_announcements", 0),
            },
        }
