"""
Job Postings Indicator
Tracks AI/ML job posting trends
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional
import aiohttp
import asyncio

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

JOB_SOURCES = {
    "linkedin": "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search",
    "indeed": "https://api.indeed.com/ads/apisearch",
}


class JobPostingsIndicator:
    AI_JOB_KEYWORDS = [
        "machine learning engineer",
        "AI engineer",
        "ML engineer",
        "deep learning",
        "NLP engineer",
        "computer vision engineer",
        "data scientist",
        "AI researcher",
        "LLM engineer",
        "MLOps engineer",
        "AI product manager",
        "AI infrastructure",
    ]

    def __init__(self, use_mock: bool = True, use_cache: bool = True):
        self.use_mock = use_mock
        self.use_cache = use_cache

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(DATA_DIR, f"jobs_{ticker}.json")

    def _load_cache(self, ticker: str) -> Optional[dict]:
        if not self.use_cache:
            return None
        path = self._get_cache_path(ticker)
        if os.path.exists(path):
            with open(path, "r") as f:
                return json.load(f)
        return None

    def _save_cache(self, ticker: str, data: dict):
        path = self._get_cache_path(ticker)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def _generate_mock_data(self, company_name: str) -> dict:
        base_ai_jobs = random.randint(50, 500)
        week_over_week_change = random.uniform(-0.3, 0.5)

        current_ai_jobs = int(base_ai_jobs * (1 + week_over_week_change))
        total_jobs = random.randint(1000, 10000)

        return {
            "current_ai_postings": current_ai_jobs,
            "prior_ai_postings": base_ai_jobs,
            "total_postings": total_jobs,
            "ai_ratio": current_ai_jobs / total_jobs if total_jobs > 0 else 0,
            "week_over_week_change": week_over_week_change,
            "top_ai_roles": random.sample(
                self.AI_JOB_KEYWORDS, min(5, len(self.AI_JOB_KEYWORDS))
            ),
            "locations": ["San Francisco", "Seattle", "New York", "Austin", "Remote"],
            "seniority_breakdown": {
                "senior": random.randint(20, 40),
                "mid": random.randint(30, 50),
                "junior": random.randint(10, 30),
            },
        }

    async def fetch_job_postings(self, company_name: str, ticker: str) -> dict:
        cached = self._load_cache(ticker)
        if cached:
            return cached

        if self.use_mock:
            data = self._generate_mock_data(company_name)
        else:
            data = await self._fetch_real_data(company_name)

        data["timestamp"] = datetime.now().isoformat()
        self._save_cache(ticker, data)
        return data

    async def _fetch_real_data(self, company_name: str) -> dict:
        return self._generate_mock_data(company_name)

    def calculate_score(self, job_data: dict) -> float:
        wow_change = job_data.get("week_over_week_change", 0)
        ai_ratio = job_data.get("ai_ratio", 0)

        score = 0.0
        score += wow_change * 2
        score += min(ai_ratio * 10, 1.0)

        return max(-2.0, min(2.0, score))

    async def get_indicator_value(self, company_name: str, ticker: str) -> dict:
        data = await self.fetch_job_postings(company_name, ticker)
        score = self.calculate_score(data)
        return {
            "value": score,
            "details": {
                "current_ai_postings": data.get("current_ai_postings", 0),
                "wow_change": round(data.get("week_over_week_change", 0) * 100, 1),
                "ai_ratio": round(data.get("ai_ratio", 0) * 100, 2),
            },
        }
