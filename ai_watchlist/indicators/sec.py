"""
SEC Filings Indicator
Tracks 10-Q, 10-K, 8-K filings and insider trading
"""

import json
import os
from datetime import datetime, timedelta
from typing import Optional
import aiohttp
import asyncio

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


class SECFilingsIndicator:
    BASE_URL = "https://data.sec.gov"
    HEADERS = {
        "User-Agent": "AIWatchlist Research contact@example.com",
        "Accept": "application/json",
    }

    def __init__(self, use_cache: bool = True, cache_hours: int = 24):
        self.use_cache = use_cache
        self.cache_hours = cache_hours
        self._cache: dict = {}

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(DATA_DIR, f"sec_{ticker}.json")

    def _load_cache(self, ticker: str) -> Optional[dict]:
        if not self.use_cache:
            return None
        path = self._get_cache_path(ticker)
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                cached_time = datetime.fromisoformat(
                    data.get("timestamp", "2000-01-01")
                )
                if datetime.now() - cached_time < timedelta(hours=self.cache_hours):
                    return data.get("data")
        return None

    def _save_cache(self, ticker: str, data: dict):
        path = self._get_cache_path(ticker)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump({"timestamp": datetime.now().isoformat(), "data": data}, f)

    async def _fetch_sec_json(
        self, session: aiohttp.ClientSession, cik: str
    ) -> Optional[dict]:
        padded_cik = cik.zfill(10)
        url = f"{self.BASE_URL}/cgi-bin/browse-edgar?action=getcompany&CIK={padded_cik}&type=&dateb=&owner=include&count=100&output=atom"

        submissions_url = f"{self.BASE_URL}/submissions/CIK{padded_cik}.json"
        try:
            async with session.get(submissions_url, headers=self.HEADERS) as resp:
                if resp.status == 200:
                    return await resp.json()
        except Exception as e:
            print(f"Error fetching SEC data for CIK {cik}: {e}")
        return None

    async def fetch_company_filings(self, ticker: str, cik: str) -> dict:
        cached = self._load_cache(ticker)
        if cached:
            return cached

        async with aiohttp.ClientSession() as session:
            data = await self._fetch_sec_json(session, cik)

        if not data:
            return {"error": "No data found", "filings": [], "insider_trades": []}

        filings = self._parse_filings(data)
        insider = self._parse_insider(data)

        result = {
            "filings": filings,
            "insider_trades": insider,
            "recent_10k_10q": [f for f in filings if f["form"] in ["10-K", "10-Q"]][:4],
            "recent_8k": [f for f in filings if f["form"] == "8-K"][:10],
        }

        self._save_cache(ticker, result)
        return result

    def _parse_filings(self, data: dict) -> list[dict]:
        filings = []
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])
        acc_nums = recent.get("accessionNumber", [])

        for i, form in enumerate(forms[:50]):
            filings.append(
                {
                    "form": form,
                    "date": dates[i] if i < len(dates) else None,
                    "accession": acc_nums[i] if i < len(acc_nums) else None,
                }
            )
        return filings

    def _parse_insider(self, data: dict) -> list[dict]:
        insider = []
        recent = data.get("filings", {}).get("recent", {})
        forms = recent.get("form", [])
        dates = recent.get("filingDate", [])

        for i, form in enumerate(forms[:100]):
            if form in ["3", "4", "5"]:
                insider.append(
                    {"form": form, "date": dates[i] if i < len(dates) else None}
                )
        return insider

    def calculate_score(self, filings_data: dict) -> float:
        if "error" in filings_data:
            return 0.0

        score = 0.0

        recent_10q = len(filings_data.get("recent_10k_10q", []))
        score += min(recent_10q, 4) * 0.5

        recent_8k = len(filings_data.get("recent_8k", []))
        score += min(recent_8k / 2, 2) * 0.25

        insider = filings_data.get("insider_trades", [])
        form4_count = len([t for t in insider if t.get("form") == "4"])
        score += min(form4_count / 5, 2) * 0.25

        return min(score, 2.0)

    async def get_indicator_value(self, ticker: str, cik: str) -> dict:
        filings = await self.fetch_company_filings(ticker, cik)
        score = self.calculate_score(filings)
        return {
            "value": score,
            "details": {
                "recent_filings_count": len(filings.get("filings", [])),
                "recent_8k_count": len(filings.get("recent_8k", [])),
                "insider_trades_count": len(filings.get("insider_trades", [])),
            },
        }
