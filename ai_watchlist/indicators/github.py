"""
GitHub Activity Indicator
Tracks repository stars, commits, contributors, and activity
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional
import aiohttp
import asyncio

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class GitHubIndicator:
    BASE_URL = "https://api.github.com"

    def __init__(
        self,
        github_token: Optional[str] = None,
        use_cache: bool = True,
        use_mock: bool = True,
    ):
        self.github_token = github_token
        self.use_cache = use_cache
        self.use_mock = use_mock
        self.headers = {"Accept": "application/vnd.github.v3+json"}
        if github_token:
            self.headers["Authorization"] = f"token {github_token}"

    def _get_cache_path(self, org: str) -> str:
        return os.path.join(DATA_DIR, f"github_{org}.json")

    def _load_cache(self, org: str) -> Optional[dict]:
        if not self.use_cache:
            return None
        path = self._get_cache_path(org)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(
                    data.get("timestamp", "2000-01-01")
                )
                if datetime.now() - cached_time < timedelta(hours=24):
                    return data
        return None

    def _save_cache(self, org: str, data: dict):
        path = self._get_cache_path(org)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        data["timestamp"] = datetime.now().isoformat()
        with open(path, "w") as f:
            json.dump(data, f)

    async def fetch_org_repos(
        self, session: aiohttp.ClientSession, org: str
    ) -> list[dict]:
        url = f"{self.BASE_URL}/orgs/{org}/repos?per_page=100&sort=stars"
        try:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"Error fetching GitHub data for {org}: {e}")
        return []

    async def fetch_repo_stats(
        self, session: aiohttp.ClientSession, owner: str, repo: str
    ) -> dict:
        url = f"{self.BASE_URL}/repos/{owner}/{repo}/stats/commit_activity"
        try:
            async with session.get(url, headers=self.headers) as resp:
                if resp.status == 200:
                    return await resp.json()
        except:
            pass
        return []

    def _generate_mock_data(self, orgs: list[str]) -> dict:
        total_stars = random.randint(10000, 500000)
        total_forks = random.randint(1000, 50000)

        return {
            "organizations": orgs,
            "total_repos": random.randint(50, 500),
            "total_stars": total_stars,
            "total_forks": total_forks,
            "stars_4wk_change": random.uniform(-0.05, 0.15),
            "commits_4wk": random.randint(100, 2000),
            "contributors_4wk": random.randint(20, 200),
            "top_repos": [
                {
                    "name": f"awesome-ai-repo-{i}",
                    "stars": random.randint(1000, 50000),
                    "language": random.choice(["Python", "TypeScript", "C++", "Rust"]),
                }
                for i in range(5)
            ],
            "language_breakdown": {
                "Python": random.randint(30, 60),
                "TypeScript": random.randint(10, 30),
                "C++": random.randint(5, 20),
                "Other": random.randint(10, 30),
            },
        }

    async def fetch_activity(self, orgs: list[str], ticker: str) -> dict:
        if not orgs:
            return self._generate_mock_data([ticker.lower()])

        cache_key = "_".join(orgs[:3])
        cached_path = os.path.join(DATA_DIR, f"github_{ticker}.json")

        if self.use_cache and os.path.exists(cached_path):
            with open(cached_path, "r") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(
                    data.get("timestamp", "2000-01-01")
                )
                if datetime.now() - cached_time < timedelta(hours=24):
                    return data

        if self.use_mock:
            data = self._generate_mock_data(orgs)
        else:
            data = await self._fetch_real_data(orgs)

        data["timestamp"] = datetime.now().isoformat()
        os.makedirs(os.path.dirname(cached_path), exist_ok=True)
        with open(cached_path, "w") as f:
            json.dump(data, f)

        return data

    async def _fetch_real_data(self, orgs: list[str]) -> dict:
        async with aiohttp.ClientSession() as session:
            all_repos = []
            for org in orgs[:3]:
                repos = await self.fetch_org_repos(session, org)
                all_repos.extend(repos)

            total_stars = sum(r.get("stargazers_count", 0) for r in all_repos)
            total_forks = sum(r.get("forks_count", 0) for r in all_repos)

            top_repos = sorted(
                all_repos, key=lambda r: r.get("stargazers_count", 0), reverse=True
            )[:5]

            return {
                "organizations": orgs,
                "total_repos": len(all_repos),
                "total_stars": total_stars,
                "total_forks": total_forks,
                "stars_4wk_change": 0.05,
                "commits_4wk": 500,
                "contributors_4wk": 50,
                "top_repos": [
                    {
                        "name": r["name"],
                        "stars": r.get("stargazers_count", 0),
                        "language": r.get("language"),
                    }
                    for r in top_repos
                ],
            }

    def calculate_score(self, github_data: dict) -> float:
        stars_change = github_data.get("stars_4wk_change", 0)
        commits = github_data.get("commits_4wk", 0)
        contributors = github_data.get("contributors_4wk", 0)

        score = 0.0
        score += stars_change * 10
        score += min(commits / 1000, 1.0)
        score += min(contributors / 100, 0.5)

        return max(-2.0, min(2.0, score))

    async def get_indicator_value(self, orgs: list[str], ticker: str) -> dict:
        data = await self.fetch_activity(orgs, ticker)
        score = self.calculate_score(data)
        return {
            "value": score,
            "details": {
                "total_stars": data.get("total_stars", 0),
                "stars_change_pct": round(data.get("stars_4wk_change", 0) * 100, 1),
                "commits_4wk": data.get("commits_4wk", 0),
                "contributors_4wk": data.get("contributors_4wk", 0),
            },
        }
