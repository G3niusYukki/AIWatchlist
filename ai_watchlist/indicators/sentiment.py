"""
Employee Sentiment Indicator
Tracks Glassdoor ratings, Blind discussions, and employee feedback
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

SENTIMENT_KEYWORDS = {
    "positive": [
        "great culture",
        "innovative",
        "exciting projects",
        "good compensation",
        "growth",
    ],
    "negative": [
        "overworked",
        "burnout",
        "layoffs",
        "toxic",
        "micromanagement",
        "restructuring",
    ],
}


class EmployeeSentimentIndicator:
    def __init__(self, use_mock: bool = True, use_cache: bool = True):
        self.use_mock = use_mock
        self.use_cache = use_cache

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(DATA_DIR, f"sentiment_{ticker}.json")

    def _generate_mock_data(self, company_name: str) -> dict:
        base_rating = random.uniform(3.5, 4.5)
        rating_change = random.uniform(-0.3, 0.3)

        return {
            "glassdoor_rating": round(base_rating, 1),
            "rating_change_4wk": round(rating_change, 2),
            "recommend_to_friend": random.uniform(0.6, 0.9),
            "ceo_approval": random.uniform(0.5, 0.95),
            "review_count_4wk": random.randint(10, 100),
            "ai_related_reviews": random.randint(5, 50),
            "positive_mentions": random.randint(20, 80),
            "negative_mentions": random.randint(5, 40),
            "compensation_trend": random.choice(["increasing", "stable", "stable"]),
            "work_life_balance_score": random.uniform(3.0, 4.5),
            "culture_score": random.uniform(3.5, 4.5),
            "career_opportunities_score": random.uniform(3.5, 4.5),
            "top_positive_themes": ["AI projects", "Smart colleagues", "Good benefits"],
            "top_negative_themes": ["Long hours", "Fast pace", "High expectations"],
        }

    async def fetch_sentiment(self, company_name: str, ticker: str) -> dict:
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

    def calculate_score(self, sentiment_data: dict) -> float:
        rating = sentiment_data.get("glassdoor_rating", 3.5)
        rating_change = sentiment_data.get("rating_change_4wk", 0)
        recommend = sentiment_data.get("recommend_to_friend", 0.7)
        positive = sentiment_data.get("positive_mentions", 1)
        negative = sentiment_data.get("negative_mentions", 1)

        score = 0.0
        score += (rating - 3.5) * 1.5
        score += rating_change * 2
        score += (recommend - 0.7) * 2
        score += (positive / (positive + negative) - 0.5) * 1.5

        return max(-2.0, min(2.0, score))

    async def get_indicator_value(self, company_name: str, ticker: str) -> dict:
        data = await self.fetch_sentiment(company_name, ticker)
        score = self.calculate_score(data)
        return {
            "value": score,
            "details": {
                "rating": data.get("glassdoor_rating", 0),
                "rating_change": data.get("rating_change_4wk", 0),
                "recommend_pct": round(data.get("recommend_to_friend", 0) * 100, 1),
                "ceo_approval": round(data.get("ceo_approval", 0) * 100, 1),
            },
        }
