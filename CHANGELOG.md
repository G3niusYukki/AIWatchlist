# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

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
- Real-time price integration
- Email/notification alerts for signal changes
- Web dashboard
- Additional data source integrations
- Backtesting capabilities
- Sector comparison analysis
