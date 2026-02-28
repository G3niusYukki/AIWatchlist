"""
Real-time Price Integration using yfinance
"""

import asyncio
from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json
import os

try:
    import yfinance as yf

    YFINANCE_AVAILABLE = True
except ImportError:
    YFINANCE_AVAILABLE = False


@dataclass
class PriceData:
    ticker: str
    current_price: float
    previous_close: float
    day_change: float
    day_change_pct: float
    week_change_pct: float
    month_change_pct: float
    volume: int
    avg_volume: int
    market_cap: float
    pe_ratio: Optional[float]
    fifty_day_ma: float
    two_hundred_day_ma: float
    fifty_two_week_high: float
    fifty_two_week_low: float
    above_50dma: bool
    above_200dma: bool
    timestamp: datetime

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "current_price": round(self.current_price, 2),
            "previous_close": round(self.previous_close, 2),
            "day_change": round(self.day_change, 2),
            "day_change_pct": round(self.day_change_pct, 2),
            "week_change_pct": round(self.week_change_pct, 2),
            "month_change_pct": round(self.month_change_pct, 2),
            "volume": self.volume,
            "avg_volume": self.avg_volume,
            "market_cap": self.market_cap,
            "pe_ratio": self.pe_ratio,
            "fifty_day_ma": round(self.fifty_day_ma, 2),
            "two_hundred_day_ma": round(self.two_hundred_day_ma, 2),
            "above_50dma": self.above_50dma,
            "above_200dma": self.above_200dma,
            "fifty_two_week_high": round(self.fifty_two_week_high, 2),
            "fifty_two_week_low": round(self.fifty_two_week_low, 2),
            "timestamp": self.timestamp.isoformat(),
        }


class PriceIntegrator:
    def __init__(self, use_cache: bool = True, cache_hours: int = 1):
        self.use_cache = use_cache
        self.cache_hours = cache_hours
        self._cache: dict = {}

        if not YFINANCE_AVAILABLE:
            print("Warning: yfinance not installed. Price data will be mocked.")

    def _get_cache_path(self, ticker: str) -> str:
        return os.path.join(
            os.path.dirname(__file__), "..", "data", f"price_{ticker}.json"
        )

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
                hours_diff = (datetime.now() - cached_time).total_seconds() / 3600
                if hours_diff < self.cache_hours:
                    return data
        return None

    def _save_cache(self, ticker: str, data: dict):
        path = self._get_cache_path(ticker)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            json.dump(data, f)

    def _generate_mock_data(self, ticker: str) -> PriceData:
        import random

        base_price = random.uniform(50, 500)
        day_change = random.uniform(-5, 5)

        return PriceData(
            ticker=ticker,
            current_price=base_price,
            previous_close=base_price - day_change,
            day_change=day_change,
            day_change_pct=(day_change / (base_price - day_change)) * 100
            if base_price != day_change
            else 0,
            week_change_pct=random.uniform(-10, 15),
            month_change_pct=random.uniform(-20, 30),
            volume=random.randint(1000000, 50000000),
            avg_volume=random.randint(5000000, 30000000),
            market_cap=random.uniform(1e9, 3e12),
            pe_ratio=random.uniform(15, 80) if random.random() > 0.2 else None,
            fifty_day_ma=base_price * random.uniform(0.9, 1.1),
            two_hundred_day_ma=base_price * random.uniform(0.8, 1.2),
            fifty_two_week_high=base_price * random.uniform(1.1, 1.5),
            fifty_two_week_low=base_price * random.uniform(0.6, 0.9),
            above_50dma=random.choice([True, False]),
            above_200dma=random.choice([True, False]),
            timestamp=datetime.now(),
        )

    async def fetch_price(self, ticker: str) -> PriceData:
        cached = self._load_cache(ticker)
        if cached:
            return PriceData(
                **{**cached, "timestamp": datetime.fromisoformat(cached["timestamp"])}
            )

        if not YFINANCE_AVAILABLE:
            return self._generate_mock_data(ticker)

        loop = asyncio.get_event_loop()

        def _fetch():
            try:
                stock = yf.Ticker(ticker)
                info = stock.info
                hist = stock.history(period="1mo")

                current_price = info.get("currentPrice") or info.get(
                    "regularMarketPrice", 0
                )
                previous_close = info.get("previousClose", current_price)
                day_change = current_price - previous_close if previous_close else 0

                if len(hist) >= 5:
                    week_ago = hist["Close"].iloc[-5]
                    week_change_pct = ((current_price - week_ago) / week_ago) * 100
                else:
                    week_change_pct = 0

                if len(hist) >= 22:
                    month_ago = hist["Close"].iloc[0]
                    month_change_pct = ((current_price - month_ago) / month_ago) * 100
                else:
                    month_change_pct = 0

                fifty_dma = info.get("fiftyDayAverage", 0)
                two_hundred_dma = info.get("twoHundredDayAverage", 0)

                return PriceData(
                    ticker=ticker,
                    current_price=current_price,
                    previous_close=previous_close,
                    day_change=day_change,
                    day_change_pct=(day_change / previous_close * 100)
                    if previous_close
                    else 0,
                    week_change_pct=week_change_pct,
                    month_change_pct=month_change_pct,
                    volume=info.get("volume", 0),
                    avg_volume=info.get("averageVolume", 0),
                    market_cap=info.get("marketCap", 0),
                    pe_ratio=info.get("trailingPE"),
                    fifty_day_ma=fifty_dma,
                    two_hundred_day_ma=two_hundred_dma,
                    fifty_two_week_high=info.get("fiftyTwoWeekHigh", 0),
                    fifty_two_week_low=info.get("fiftyTwoWeekLow", 0),
                    above_50dma=current_price > fifty_dma if fifty_dma else False,
                    above_200dma=current_price > two_hundred_dma
                    if two_hundred_dma
                    else False,
                    timestamp=datetime.now(),
                )
            except Exception as e:
                print(f"Error fetching price for {ticker}: {e}")
                return self._generate_mock_data(ticker)

        result = await loop.run_in_executor(None, _fetch)

        self._save_cache(ticker, result.to_dict())
        return result

    async def fetch_prices(self, tickers: list[str]) -> dict[str, PriceData]:
        tasks = [self.fetch_price(t) for t in tickers]
        results = await asyncio.gather(*tasks)
        return {r.ticker: r for r in results}

    def calculate_price_momentum_score(self, price_data: PriceData) -> float:
        score = 0.0

        if price_data.above_50dma:
            score += 0.5
        if price_data.above_200dma:
            score += 0.5

        score += max(-1, min(1, price_data.week_change_pct / 10))
        score += max(-1, min(1, price_data.month_change_pct / 20))

        if price_data.fifty_day_ma > price_data.two_hundred_day_ma:
            score += 0.3

        return max(-2, min(2, score))
