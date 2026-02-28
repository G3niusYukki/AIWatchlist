# AI Company Watchlist

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/G3niusYukki/AIWatchlist.svg)](https://github.com/G3niusYukki/AIWatchlist/stargazers)

A comprehensive tool for tracking leading indicators of public AI companies to identify potential investment opportunities. Monitor SEC filings, job postings, GitHub activity, executive appearances, employee sentiment, government contracts, and more for 20 major AI-focused public companies.

## Features

- **6 Core Weighted Leading Indicators**:
  - SEC Filings (10-K, 10-Q, 8-K, Form 4 insider trading)
  - AI/ML Job Posting Trends
  - GitHub Repository Activity (stars, commits, contributors)
  - Executive Public Appearances & Sentiment
  - Employee Sentiment (Glassdoor-style metrics)
  - Government Contract Awards

- **Real-time Price Integration** (NEW in v2.0):
  - Current prices, day/week/month changes
  - Moving average analysis (50DMA, 200DMA)
  - 52-week high/low tracking
  - Volume and market cap data

- **Alert System** (NEW in v2.0):
  - Signal upgrade/downgrade notifications
  - Email, Slack, Discord, and webhook support
  - Configurable thresholds

- **Web Dashboard** (NEW in v2.0):
  - Real-time monitoring interface
  - Interactive charts and tables
  - WebSocket updates
  - Company detail views

- **Additional Data Sources** (NEW in v2.0):
  - News sentiment analysis
  - Earnings call data
  - Social media sentiment
  - Patent filings
  - Analyst ratings

- **Backtesting** (NEW in v2.0):
  - Historical signal performance
  - Multiple strategy comparison
  - Win rate, drawdown, Sharpe ratio

- **Sector Analysis** (NEW in v2.0):
  - Sector-level aggregation
  - Cross-sector comparison
  - Rotation signals

## Tracked Companies

| Ticker | Company | Sector |
|--------|---------|--------|
| NVDA | NVIDIA | Semiconductors |
| AMD | AMD | Semiconductors |
| AVGO | Broadcom | Semiconductors |
| TSM | Taiwan Semiconductor | Semiconductors |
| MSFT | Microsoft | Cloud/Software |
| GOOGL | Alphabet | Cloud/Software |
| AMZN | Amazon | Cloud/Software |
| ORCL | Oracle | Cloud/Software |
| IBM | IBM | Cloud/Software |
| SNOW | Snowflake | Cloud/Software |
| NOW | ServiceNow | Cloud/Software |
| CRM | Salesforce | Cloud/Software |
| ADBE | Adobe | Cloud/Software |
| DDOG | Datadog | Cloud/Software |
| META | Meta Platforms | Social/Media |
| AAPL | Apple | Consumer Tech |
| PLTR | Palantir | Enterprise AI |
| AI | C3.ai | Enterprise AI |
| INTU | Intuit | Fintech |
| CRWD | CrowdStrike | Cybersecurity |

## Installation

```bash
# Clone the repository
git clone https://github.com/G3niusYukki/AIWatchlist.git
cd AIWatchlist

# Install dependencies
pip install -r requirements.txt
```

## Quick Start

```bash
# List all tracked companies
python -m ai_watchlist list

# Analyze all companies and generate signals
python -m ai_watchlist analyze

# Show top 10 companies with highest composite scores
python -m ai_watchlist analyze --top 10

# Analyze specific companies
python -m ai_watchlist analyze -t NVDA MSFT GOOGL

# Get detailed analysis for a specific company
python -m ai_watchlist detail NVDA

# View historical trends
python -m ai_watchlist history NVDA

# Fetch real-time prices
python -m ai_watchlist prices

# Get additional data sources
python -m ai_watchlist data NVDA

# Run backtesting
python -m ai_watchlist backtest NVDA --weeks 12

# Compare all backtest strategies
python -m ai_watchlist backtest NVDA --compare

# Sector comparison analysis
python -m ai_watchlist sectors

# Launch web dashboard
python -m ai_watchlist dashboard

# Export results
python -m ai_watchlist export --format csv
python -m ai_watchlist export --format json
```

## Web Dashboard

Launch the interactive web dashboard:

```bash
python -m ai_watchlist dashboard --port 8000
```

Then open http://localhost:8000 in your browser.

Features:
- Real-time signal updates
- Interactive charts
- Company detail modals
- Search and filtering
- WebSocket notifications

## Scoring Methodology

### Indicator Weights

| Indicator | Weight | Rationale |
|-----------|--------|-----------|
| SEC Filings | 25% | Material, audited data |
| Government Contracts | 25% | Revenue certainty |
| Job Postings | 15% | Leading indicator |
| Exec Appearances | 15% | Strategic signaling |
| GitHub Activity | 10% | Developer ecosystem |
| Employee Sentiment | 10% | Culture/institutional health |

### Signal Thresholds

| Score Range | Signal | Interpretation |
|-------------|--------|----------------|
| > +2.0 | STRONG BUY | Significant bullish momentum |
| +1.0 to +2.0 | BUY | Positive indicators |
| -1.0 to +1.0 | HOLD | Neutral, monitor |
| -1.0 to -2.0 | SELL | Negative indicators |
| < -2.0 | STRONG SELL | Significant bearish signals |

## Alert Configuration

```python
from ai_watchlist import AlertManager, AlertConfig

config = AlertConfig(
    email_enabled=True,
    email_smtp_host="smtp.gmail.com",
    email_username="your@email.com",
    email_password="your-app-password",
    email_recipients=["recipient@email.com"],
    
    slack_enabled=True,
    slack_webhook_url="https://hooks.slack.com/services/...",
    
    alert_on_signal_change=True,
    alert_on_strong_buy=True,
)

alert_manager = AlertManager(config)
```

## API Usage

```python
import asyncio
from ai_watchlist import AIWatchlist, Backtester, SectorAnalyzer
from ai_watchlist.indicators import PriceIntegrator, DataIntegrator

async def main():
    # Initialize
    watchlist = AIWatchlist(use_mock=True)
    prices = PriceIntegrator()
    backtester = Backtester(initial_capital=100000)
    sectors = SectorAnalyzer()
    
    # Analyze all companies
    scores = await watchlist.analyze_all()
    for score in scores[:5]:
        print(f"{score.ticker}: {score.composite_score:.2f} - {score.signal.value}")
    
    # Get prices
    price = await prices.fetch_price("NVDA")
    print(f"NVDA: ${price.current_price:.2f} ({price.day_change_pct:+.2f}%)")
    
    # Run backtest
    result = await backtester.run_backtest("NVDA", weeks=12)
    print(f"Return: {result['total_return_pct']:.2f}%")
    
    # Sector analysis
    analysis = await sectors.analyze_sectors()
    print(f"Top sector: {analysis['rankings']['by_sector_score'][0]}")

asyncio.run(main())
```

## Project Structure

```
ai_watchlist/
├── __init__.py
├── __main__.py           # CLI entry point
├── config.py             # Companies, weights, thresholds
├── models.py             # Data classes
├── watchlist.py          # Main AIWatchlist class
├── scoring.py            # Scoring engine
├── alerts.py             # Alert system (NEW)
├── backtest.py           # Backtesting (NEW)
├── sectors.py            # Sector analysis (NEW)
├── dashboard/            # Web dashboard (NEW)
│   ├── app.py
│   ├── templates/
│   └── static/
├── data/
│   └── historical/
└── indicators/
    ├── __init__.py
    ├── sec.py
    ├── jobs.py
    ├── github.py
    ├── executives.py
    ├── sentiment.py
    ├── contracts.py
    ├── prices.py          # Price integration (NEW)
    └── data_sources.py    # Additional sources (NEW)
```

## Example Output

```
================================================================================
AI COMPANY WATCHLIST - WEEKLY SIGNALS REPORT
Generated: 2026-02-28 13:20:20
================================================================================

SIGNAL SUMMARY:
----------------------------------------
  STRONG BUY      :   2 companies
  BUY             :  12 companies
  HOLD            :   5 companies
  SELL            :   1 companies

================================================================================
TOP 10 RANKINGS (by composite score)
================================================================================
Rank Ticker    Score         Signal    SEC   Jobs GitHub   Exec   Sent   Govt
--------------------------------------------------------------------------------
   1   NVDA    1.709            BUY   1.88   0.74   1.79   1.67   2.00   2.00
   2   META    1.661            BUY   1.25   1.01   2.00   2.00   1.97   2.00
   3    AMD    1.652            BUY   2.00   1.03   1.16   1.50   1.58   2.00
   ...
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## Disclaimer

This tool is for educational and research purposes only. It does not constitute financial advice. Always do your own research before making investment decisions. Past performance and indicators do not guarantee future results.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
