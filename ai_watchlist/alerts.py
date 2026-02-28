"""
Alert System for Signal Changes
Supports email, Slack, Discord, and webhook notifications
"""

import asyncio
import json
import os
import smtplib
from dataclasses import dataclass, field
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Optional, Callable
from enum import Enum

from .models import SignalType, CompanyScore


class AlertType(Enum):
    SIGNAL_UPGRADE = "SIGNAL_UPGRADE"
    SIGNAL_DOWNGRADE = "SIGNAL_DOWNGRADE"
    STRONG_BUY = "STRONG_BUY"
    STRONG_SELL = "STRONG_SELL"
    SCORE_THRESHOLD = "SCORE_THRESHOLD"
    PRICE_ALERT = "PRICE_ALERT"


@dataclass
class Alert:
    ticker: str
    company_name: str
    alert_type: AlertType
    old_signal: Optional[SignalType]
    new_signal: SignalType
    old_score: float
    new_score: float
    message: str
    timestamp: datetime = field(default_factory=datetime.now)
    details: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "company_name": self.company_name,
            "alert_type": self.alert_type.value,
            "old_signal": self.old_signal.value if self.old_signal else None,
            "new_signal": self.new_signal.value,
            "old_score": round(self.old_score, 3),
            "new_score": round(self.new_score, 3),
            "message": self.message,
            "timestamp": self.timestamp.isoformat(),
            "details": self.details,
        }


@dataclass
class AlertConfig:
    email_enabled: bool = False
    email_smtp_host: str = "smtp.gmail.com"
    email_smtp_port: int = 587
    email_username: str = ""
    email_password: str = ""
    email_recipients: list[str] = field(default_factory=list)

    slack_enabled: bool = False
    slack_webhook_url: str = ""

    discord_enabled: bool = False
    discord_webhook_url: str = ""

    webhook_enabled: bool = False
    webhook_url: str = ""

    custom_callback: Optional[Callable] = None

    alert_on_signal_change: bool = True
    alert_on_strong_buy: bool = True
    alert_on_strong_sell: bool = True
    score_threshold_buy: float = 1.5
    score_threshold_sell: float = -1.5


class AlertManager:
    def __init__(self, config: AlertConfig, history_dir: str = None):
        self.config = config
        self.history_dir = history_dir or os.path.join(
            os.path.dirname(__file__), "..", "data", "alerts"
        )
        self.signal_history: dict[str, SignalType] = {}
        self.score_history: dict[str, float] = {}
        os.makedirs(self.history_dir, exist_ok=True)
        self._load_history()

    def _get_history_path(self) -> str:
        return os.path.join(self.history_dir, "signal_history.json")

    def _load_history(self):
        path = self._get_history_path()
        if os.path.exists(path):
            with open(path, "r") as f:
                data = json.load(f)
                for ticker, signal in data.get("signals", {}).items():
                    self.signal_history[ticker] = SignalType(signal)
                self.score_history = data.get("scores", {})

    def _save_history(self):
        path = self._get_history_path()
        data = {
            "signals": {t: s.value for t, s in self.signal_history.items()},
            "scores": self.score_history,
            "updated": datetime.now().isoformat(),
        }
        with open(path, "w") as f:
            json.dump(data, f, indent=2)

    def check_for_alerts(self, score: CompanyScore) -> list[Alert]:
        alerts = []
        ticker = score.ticker

        old_signal = self.signal_history.get(ticker)
        old_score = self.score_history.get(ticker, 0.0)

        if old_signal and self.config.alert_on_signal_change:
            if self._is_upgrade(old_signal, score.signal):
                alert = Alert(
                    ticker=ticker,
                    company_name=score.company_name,
                    alert_type=AlertType.SIGNAL_UPGRADE,
                    old_signal=old_signal,
                    new_signal=score.signal,
                    old_score=old_score,
                    new_score=score.composite_score,
                    message=f"🟢 {score.company_name} ({ticker}) upgraded from {old_signal.value} to {score.signal.value} (Score: {score.composite_score:.2f})",
                )
                alerts.append(alert)

            elif self._is_downgrade(old_signal, score.signal):
                alert = Alert(
                    ticker=ticker,
                    company_name=score.company_name,
                    alert_type=AlertType.SIGNAL_DOWNGRADE,
                    old_signal=old_signal,
                    new_signal=score.signal,
                    old_score=old_score,
                    new_score=score.composite_score,
                    message=f"🔴 {score.company_name} ({ticker}) downgraded from {old_signal.value} to {score.signal.value} (Score: {score.composite_score:.2f})",
                )
                alerts.append(alert)

        if self.config.alert_on_strong_buy and score.signal == SignalType.STRONG_BUY:
            if old_signal != SignalType.STRONG_BUY:
                alert = Alert(
                    ticker=ticker,
                    company_name=score.company_name,
                    alert_type=AlertType.STRONG_BUY,
                    old_signal=old_signal,
                    new_signal=score.signal,
                    old_score=old_score,
                    new_score=score.composite_score,
                    message=f"🚀 {score.company_name} ({ticker}) triggered STRONG BUY signal! (Score: {score.composite_score:.2f})",
                )
                alerts.append(alert)

        if self.config.alert_on_strong_sell and score.signal == SignalType.STRONG_SELL:
            if old_signal != SignalType.STRONG_SELL:
                alert = Alert(
                    ticker=ticker,
                    company_name=score.company_name,
                    alert_type=AlertType.STRONG_SELL,
                    old_signal=old_signal,
                    new_signal=score.signal,
                    old_score=old_score,
                    new_score=score.composite_score,
                    message=f"⚠️ {score.company_name} ({ticker}) triggered STRONG SELL signal! (Score: {score.composite_score:.2f})",
                )
                alerts.append(alert)

        if (
            score.composite_score >= self.config.score_threshold_buy
            and old_score < self.config.score_threshold_buy
        ):
            alert = Alert(
                ticker=ticker,
                company_name=score.company_name,
                alert_type=AlertType.SCORE_THRESHOLD,
                old_signal=old_signal,
                new_signal=score.signal,
                old_score=old_score,
                new_score=score.composite_score,
                message=f"📈 {score.company_name} ({ticker}) crossed buy threshold! Score: {old_score:.2f} → {score.composite_score:.2f}",
            )
            alerts.append(alert)

        if (
            score.composite_score <= self.config.score_threshold_sell
            and old_score > self.config.score_threshold_sell
        ):
            alert = Alert(
                ticker=ticker,
                company_name=score.company_name,
                alert_type=AlertType.SCORE_THRESHOLD,
                old_signal=old_signal,
                new_signal=score.signal,
                old_score=old_score,
                new_score=score.composite_score,
                message=f"📉 {score.company_name} ({ticker}) crossed sell threshold! Score: {old_score:.2f} → {score.composite_score:.2f}",
            )
            alerts.append(alert)

        self.signal_history[ticker] = score.signal
        self.score_history[ticker] = score.composite_score
        self._save_history()

        return alerts

    def _is_upgrade(self, old: SignalType, new: SignalType) -> bool:
        order = [
            SignalType.STRONG_SELL,
            SignalType.SELL,
            SignalType.HOLD,
            SignalType.BUY,
            SignalType.STRONG_BUY,
        ]
        return order.index(new) > order.index(old)

    def _is_downgrade(self, old: SignalType, new: SignalType) -> bool:
        order = [
            SignalType.STRONG_SELL,
            SignalType.SELL,
            SignalType.HOLD,
            SignalType.BUY,
            SignalType.STRONG_BUY,
        ]
        return order.index(new) < order.index(old)

    async def send_alert(self, alert: Alert):
        tasks = []

        if self.config.email_enabled:
            tasks.append(self._send_email(alert))

        if self.config.slack_enabled:
            tasks.append(self._send_slack(alert))

        if self.config.discord_enabled:
            tasks.append(self._send_discord(alert))

        if self.config.webhook_enabled:
            tasks.append(self._send_webhook(alert))

        if self.config.custom_callback:
            tasks.append(self._run_callback(alert))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_alerts(self, alerts: list[Alert]):
        for alert in alerts:
            await self.send_alert(alert)

    async def _send_email(self, alert: Alert):
        if not self.config.email_recipients:
            return

        msg = MIMEMultipart("alternative")
        msg["Subject"] = (
            f"AI Watchlist Alert: {alert.ticker} - {alert.alert_type.value}"
        )
        msg["From"] = self.config.email_username
        msg["To"] = ", ".join(self.config.email_recipients)

        text = f"""
AI Watchlist Alert

{alert.message}

Details:
- Ticker: {alert.ticker}
- Company: {alert.company_name}
- Alert Type: {alert.alert_type.value}
- Previous Signal: {alert.old_signal.value if alert.old_signal else "N/A"}
- New Signal: {alert.new_signal.value}
- Previous Score: {alert.old_score:.3f}
- New Score: {alert.new_score:.3f}
- Timestamp: {alert.timestamp.strftime("%Y-%m-%d %H:%M:%S")}

---
AI Watchlist - Investment Research Tool
"""

        html = f"""
<html>
<body style="font-family: Arial, sans-serif; padding: 20px;">
    <h2 style="color: #333;">AI Watchlist Alert</h2>
    <div style="background: #f5f5f5; padding: 15px; border-radius: 5px; margin: 20px 0;">
        <p style="font-size: 18px; margin: 0;">{alert.message}</p>
    </div>
    <table style="border-collapse: collapse; width: 100%;">
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Ticker</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.ticker}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Company</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.company_name}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Alert Type</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.alert_type.value}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Previous Signal</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.old_signal.value if alert.old_signal else "N/A"}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>New Signal</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.new_signal.value}</td></tr>
        <tr><td style="padding: 8px; border-bottom: 1px solid #ddd;"><strong>Score Change</strong></td><td style="padding: 8px; border-bottom: 1px solid #ddd;">{alert.old_score:.3f} → {alert.new_score:.3f}</td></tr>
    </table>
    <p style="color: #888; font-size: 12px; margin-top: 20px;">AI Watchlist - Investment Research Tool</p>
</body>
</html>
"""

        msg.attach(MIMEText(text, "plain"))
        msg.attach(MIMEText(html, "html"))

        loop = asyncio.get_event_loop()

        def _send():
            try:
                with smtplib.SMTP(
                    self.config.email_smtp_host, self.config.email_smtp_port
                ) as server:
                    server.starttls()
                    server.login(self.config.email_username, self.config.email_password)
                    server.sendmail(
                        self.config.email_username,
                        self.config.email_recipients,
                        msg.as_string(),
                    )
            except Exception as e:
                print(f"Error sending email: {e}")

        await loop.run_in_executor(None, _send)

    async def _send_slack(self, alert: Alert):
        import aiohttp

        color = {
            AlertType.SIGNAL_UPGRADE: "#36a64f",
            AlertType.SIGNAL_DOWNGRADE: "#dc3545",
            AlertType.STRONG_BUY: "#00ff00",
            AlertType.STRONG_SELL: "#ff0000",
            AlertType.SCORE_THRESHOLD: "#007bff",
        }.get(alert.alert_type, "#888888")

        payload = {
            "attachments": [
                {
                    "color": color,
                    "title": f"AI Watchlist Alert: {alert.ticker}",
                    "text": alert.message,
                    "fields": [
                        {
                            "title": "Company",
                            "value": alert.company_name,
                            "short": True,
                        },
                        {
                            "title": "Signal",
                            "value": f"{alert.old_signal.value if alert.old_signal else 'N/A'} → {alert.new_signal.value}",
                            "short": True,
                        },
                        {
                            "title": "Score",
                            "value": f"{alert.old_score:.2f} → {alert.new_score:.2f}",
                            "short": True,
                        },
                        {
                            "title": "Alert Type",
                            "value": alert.alert_type.value,
                            "short": True,
                        },
                    ],
                    "footer": "AI Watchlist",
                    "ts": int(alert.timestamp.timestamp()),
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.slack_webhook_url, json=payload
            ) as resp:
                if resp.status != 200:
                    print(f"Slack webhook failed: {resp.status}")

    async def _send_discord(self, alert: Alert):
        import aiohttp

        color = {
            AlertType.SIGNAL_UPGRADE: 3581519,
            AlertType.SIGNAL_DOWNGRADE: 14431557,
            AlertType.STRONG_BUY: 65280,
            AlertType.STRONG_SELL: 16711680,
            AlertType.SCORE_THRESHOLD: 3447003,
        }.get(alert.alert_type, 8421504)

        payload = {
            "embeds": [
                {
                    "title": f"AI Watchlist Alert: {alert.ticker}",
                    "description": alert.message,
                    "color": color,
                    "fields": [
                        {
                            "name": "Company",
                            "value": alert.company_name,
                            "inline": True,
                        },
                        {
                            "name": "Signal",
                            "value": f"{alert.old_signal.value if alert.old_signal else 'N/A'} → {alert.new_signal.value}",
                            "inline": True,
                        },
                        {
                            "name": "Score",
                            "value": f"{alert.old_score:.2f} → {alert.new_score:.2f}",
                            "inline": True,
                        },
                    ],
                    "footer": {"text": "AI Watchlist"},
                    "timestamp": alert.timestamp.isoformat(),
                }
            ]
        }

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.discord_webhook_url, json=payload
            ) as resp:
                if resp.status != 204:
                    print(f"Discord webhook failed: {resp.status}")

    async def _send_webhook(self, alert: Alert):
        import aiohttp

        async with aiohttp.ClientSession() as session:
            async with session.post(
                self.config.webhook_url, json=alert.to_dict()
            ) as resp:
                if resp.status not in [200, 201, 202]:
                    print(f"Custom webhook failed: {resp.status}")

    async def _run_callback(self, alert: Alert):
        if asyncio.iscoroutinefunction(self.config.custom_callback):
            await self.config.custom_callback(alert)
        else:
            self.config.custom_callback(alert)
