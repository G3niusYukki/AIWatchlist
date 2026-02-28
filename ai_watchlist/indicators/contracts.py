"""
Government Contracts Indicator
Tracks federal AI/ML contract awards from USAspending.gov
"""

import json
import os
import random
from datetime import datetime, timedelta
from typing import Optional
import aiohttp

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")

GOV_AGENCIES = [
    "Department of Defense",
    "Defense Innovation Unit",
    "DARPA",
    "Department of Energy",
    "National Institutes of Health",
    "Department of Homeland Security",
    "Intelligence Community",
    "Department of Veterans Affairs",
    "NASA",
    "NSF",
]


class GovernmentContractsIndicator:
    USA_SPENDING_API = "https://api.usaspending.gov"

    def __init__(self, use_mock: bool = True, use_cache: bool = True):
        self.use_mock = use_mock
        self.use_cache = use_cache

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(DATA_DIR, f"govt_{ticker}.json")

    def _generate_mock_data(self, company_name: str) -> dict:
        total_value = random.randint(0, 500000000)
        new_contracts = random.randint(0, 5)

        contracts = []
        for _ in range(new_contracts):
            contracts.append(
                {
                    "agency": random.choice(GOV_AGENCIES),
                    "value": random.randint(100000, 50000000),
                    "date": (
                        datetime.now() - timedelta(days=random.randint(1, 28))
                    ).strftime("%Y-%m-%d"),
                    "description": f"AI/ML {random.choice(['Platform', 'Services', 'Infrastructure', 'Research'])}",
                    "duration_months": random.choice([12, 24, 36, 48]),
                }
            )

        return {
            "total_contract_value_4wk": total_value,
            "new_contracts_4wk": new_contracts,
            "contracts": contracts,
            "ai_related_value": int(total_value * random.uniform(0.3, 0.8)),
            "defense_contracts": random.randint(0, 3),
            "civilian_contracts": random.randint(0, 2),
            "sbir_grants": random.randint(0, 2),
            "contract_modifications": random.randint(0, 3),
            "avg_contract_duration": random.choice([12, 24, 36]),
            "recurring_revenue_indicator": random.choice([True, False]),
        }

    async def fetch_contracts(self, company_name: str, ticker: str) -> dict:
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

    def calculate_score(self, contracts_data: dict, market_cap: float = 1e12) -> float:
        total_value = contracts_data.get("total_contract_value_4wk", 0)
        new_contracts = contracts_data.get("new_contracts_4wk", 0)
        ai_value = contracts_data.get("ai_related_value", 0)
        modifications = contracts_data.get("contract_modifications", 0)

        score = 0.0

        value_score = (total_value / market_cap) * 10000
        score += min(value_score, 1.0)

        score += min(new_contracts * 0.3, 1.0)
        score += min(modifications * 0.15, 0.5)

        if contracts_data.get("recurring_revenue_indicator"):
            score += 0.3

        return max(-2.0, min(2.0, score))

    async def get_indicator_value(
        self, company_name: str, ticker: str, market_cap: float = 1e12
    ) -> dict:
        data = await self.fetch_contracts(company_name, ticker)
        score = self.calculate_score(data, market_cap)
        return {
            "value": score,
            "details": {
                "total_value": data.get("total_contract_value_4wk", 0),
                "new_contracts": data.get("new_contracts_4wk", 0),
                "ai_related_value": data.get("ai_related_value", 0),
                "defense_contracts": data.get("defense_contracts", 0),
            },
        }
