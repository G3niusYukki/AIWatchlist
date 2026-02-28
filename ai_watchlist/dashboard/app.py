"""
Web Dashboard for AI Watchlist
FastAPI-based real-time monitoring dashboard
"""

import asyncio
import json
import os
from datetime import datetime
from typing import Optional

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from ..watchlist import AIWatchlist
from ..models import SignalType
from ..indicators.prices import PriceIntegrator
from ..alerts import AlertManager, AlertConfig


app = FastAPI(
    title="AI Watchlist Dashboard",
    description="Real-time monitoring dashboard for AI company indicators",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(__file__)
app.mount(
    "/static", StaticFiles(directory=os.path.join(BASE_DIR, "static")), name="static"
)
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

watchlist: Optional[AIWatchlist] = None
price_integrator: Optional[PriceIntegrator] = None
alert_manager: Optional[AlertManager] = None
latest_scores: list = []
latest_prices: dict = {}


class ConnectionManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_json(message)
            except:
                pass


manager = ConnectionManager()


def init_dashboard(use_mock: bool = True, alert_config: Optional[AlertConfig] = None):
    global watchlist, price_integrator, alert_manager

    watchlist = AIWatchlist(use_mock=use_mock, use_cache=True)
    price_integrator = PriceIntegrator(use_cache=True)
    alert_manager = AlertManager(alert_config or AlertConfig())


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/api/companies")
async def get_companies():
    from ..config import COMPANIES

    return {"companies": COMPANIES}


@app.get("/api/analyze")
async def analyze_all():
    global latest_scores

    scores = await watchlist.analyze_all()
    latest_scores = scores

    alerts = []
    for score in scores:
        score_alerts = alert_manager.check_for_alerts(score)
        alerts.extend(score_alerts)

    if alerts:
        await alert_manager.send_alerts(alerts)
        await manager.broadcast(
            {"type": "alerts", "alerts": [a.to_dict() for a in alerts]}
        )

    return {
        "generated_at": datetime.now().isoformat(),
        "scores": [s.to_dict() for s in scores],
        "summary": {
            "strong_buy": len([s for s in scores if s.signal == SignalType.STRONG_BUY]),
            "buy": len([s for s in scores if s.signal == SignalType.BUY]),
            "hold": len([s for s in scores if s.signal == SignalType.HOLD]),
            "sell": len([s for s in scores if s.signal == SignalType.SELL]),
            "strong_sell": len(
                [s for s in scores if s.signal == SignalType.STRONG_SELL]
            ),
        },
    }


@app.get("/api/analyze/{ticker}")
async def analyze_company(ticker: str):
    from ..config import COMPANIES

    company = next((c for c in COMPANIES if c["ticker"] == ticker.upper()), None)
    if not company:
        return {"error": f"Company {ticker} not found"}

    score = await watchlist.analyze_company(company)
    alerts = alert_manager.check_for_alerts(score)

    if alerts:
        await alert_manager.send_alerts(alerts)

    return {"score": score.to_dict(), "alerts": [a.to_dict() for a in alerts]}


@app.get("/api/prices")
async def get_prices():
    from ..config import COMPANIES

    tickers = [c["ticker"] for c in COMPANIES]
    global latest_prices
    latest_prices = await price_integrator.fetch_prices(tickers)

    return {"prices": {t: p.to_dict() for t, p in latest_prices.items()}}


@app.get("/api/prices/{ticker}")
async def get_price(ticker: str):
    price = await price_integrator.fetch_price(ticker.upper())
    return {"price": price.to_dict()}


@app.get("/api/history/{ticker}")
async def get_history(ticker: str):
    history = watchlist.get_company_history(ticker.upper())
    return {"ticker": ticker.upper(), "history": history}


@app.get("/api/alerts")
async def get_alerts():
    alerts_dir = os.path.join(os.path.dirname(__file__), "..", "data", "alerts")
    history_path = os.path.join(alerts_dir, "signal_history.json")

    if os.path.exists(history_path):
        with open(history_path, "r") as f:
            return json.load(f)
    return {"signals": {}, "scores": {}}


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_json({"type": "pong"})
            elif data == "refresh":
                scores = await watchlist.analyze_all()
                await websocket.send_json(
                    {"type": "scores", "scores": [s.to_dict() for s in scores]}
                )
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.get("/api/backtest")
async def run_backtest(ticker: str = Query(...), weeks: int = Query(12, ge=4, le=52)):
    from ..backtest import Backtester

    backtester = Backtester()
    result = await backtester.run_backtest(ticker.upper(), weeks=weeks)
    return result


@app.get("/api/sectors")
async def sector_comparison():
    from ..sectors import SectorAnalyzer

    analyzer = SectorAnalyzer()
    comparison = await analyzer.analyze_sectors()
    return comparison


def run_dashboard(
    host: str = "0.0.0.0",
    port: int = 8000,
    use_mock: bool = True,
    alert_config: Optional[AlertConfig] = None,
):
    init_dashboard(use_mock=use_mock, alert_config=alert_config)
    uvicorn.run(app, host=host, port=port)


if __name__ == "__main__":
    run_dashboard()
