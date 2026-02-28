# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2026-02-28

### Added

#### Real-time Price Integration
- `PriceIntegrator` class for fetching stock prices via yfinance
- Current price, day/week/month changes
- 50-day and 200-day moving average tracking
- 52-week high/low data
- Volume and market cap metrics
- `python -m ai_watchlist prices` CLI command

#### Alert System
- `AlertManager` for signal change notifications
- Email notifications (SMTP support)
- Slack webhook integration
- Discord webhook integration
- Custom webhook support
- Configurable alert thresholds
- Signal upgrade/downgrade detection
- Strong buy/sell alerts

#### Web Dashboard
- FastAPI-based real-time dashboard
- Interactive HTML/CSS/JS interface
- Chart.js integration for visualizations
- WebSocket support for live updates
- Company detail modals
- Search and filtering
- Responsive design
- `python -m ai_watchlist dashboard` CLI command

#### Additional Data Sources
- `DataIntegrator` for aggregating multiple sources
- `NewsIntegrator` for news sentiment (NewsAPI compatible)
- `EarningsIntegrator` for earnings call data
- `SocialSentimentIntegrator` for Twitter/Reddit analysis
- `PatentIntegrator` for patent filing tracking
- `AnalystIntegrator` for analyst ratings
- `python -m ai_watchlist data TICKER` CLI command

#### Backtesting
- `Backtester` class for historical simulation
- Multiple strategy support:
  - Signal follow
  - Strong buy only
  - Buy and hold
  - Mean reversion
- Performance metrics: win rate, Sharpe ratio, max drawdown
- Strategy comparison mode
- `python -m ai_watchlist backtest TICKER` CLI command

#### Sector Analysis
- `SectorAnalyzer` for sector-level aggregation
- 7 sector classifications:
  - Semiconductors
  - Cloud/Software
  - Social/Media
  - Consumer Tech
  - Enterprise AI
  - Fintech
  - Cybersecurity
- Sector rotation signals
- Cross-sector comparison
- Company comparison tool
- `python -m ai_watchlist sectors` CLI command

### Changed
- Updated CLI with new commands
- Enhanced company listing with sector information
- Improved data models

### Dependencies
- Added yfinance>=0.2.0
- Added fastapi>=0.100.0
- Added uvicorn>=0.23.0
- Added jinja2>=3.1.0

## [1.0.0] - 2026-02-28

### Added
- Initial release of AI Company Watchlist
- 20 pre-configured AI-focused public companies
- 6 weighted leading indicators:
  - SEC Filings (10-K, 10-Q, 8-K, Form 4)
  - AI/ML Job Posting Trends
  - GitHub Repository Activity
  - Executive Public Appearances
  - Employee Sentiment
  - Government Contract Awards
- Rolling 4-week baseline for Z-score normalization
- Composite scoring system with weighted aggregation
- Signal generation (STRONG BUY, BUY, HOLD, SELL, STRONG SELL)
- Historical tracking and trend analysis
- CLI interface with multiple commands:
  - `analyze` - Analyze companies and generate signals
  - `detail` - Detailed company breakdown
  - `history` - Historical indicator trends
  - `list` - List all tracked companies
  - `export` - Export to JSON or CSV
- Async data fetching for improved performance
- Caching system to reduce API calls
- Mock data mode for testing and demonstration
- JSON and CSV export formats
- Comprehensive documentation

### Technical Details
- Python 3.9+ support
- aiohttp for async HTTP requests
- Modular indicator architecture for easy extension
- Configurable weights and thresholds
- Type hints throughout codebase

## [Unreleased]

### Planned
- Real API integrations (NewsAPI, etc.)
- Machine learning signal enhancement
- Portfolio optimization
- Risk metrics (VaR, beta)
- Options flow analysis
- Institutional ownership tracking
- Mobile app companion
