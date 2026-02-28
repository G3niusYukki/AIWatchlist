# AI Company Watchlist

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![GitHub Stars](https://img.shields.io/github/stars/G3niusYukki/AIWatchlist.svg)](https://github.com/G3niusYukki/AIWatchlist/stargazers)

A comprehensive tool for tracking leading indicators of public AI companies to identify potential investment opportunities. Monitor SEC filings, job postings, GitHub activity, executive appearances, employee sentiment, and government contracts for 20 major AI-focused public companies.

## Features

- **6 Weighted Leading Indicators**:
  - SEC Filings (10-K, 10-Q, 8-K, Form 4 insider trading)
  - AI/ML Job Posting Trends
  - GitHub Repository Activity (stars, commits, contributors)
  - Executive Public Appearances & Sentiment
  - Employee Sentiment (Glassdoor-style metrics)
  - Government Contract Awards

- **Rolling 4-Week Baseline**: Z-score normalization for cross-indicator comparison
- **Composite Scoring System**: Weighted aggregation with signal thresholds
- **Signal Generation**: STRONG BUY, BUY, HOLD, SELL, STRONG SELL signals
- **Historical Tracking**: Trend analysis over time
- **Multiple Export Formats**: JSON and CSV

## Tracked Companies

| Ticker | Company | Primary AI Focus |
|--------|---------|------------------|
| NVDA | NVIDIA | AI chips, data center GPUs |
| MSFT | Microsoft | Azure AI, OpenAI partnership, Copilot |
| GOOGL | Alphabet | Google Cloud AI, Gemini, TPU chips |
| AMZN | Amazon | AWS AI services, Alexa, Bedrock |
| META | Meta Platforms | Llama models, AI infrastructure |
| TSM | Taiwan Semiconductor | AI chip manufacturing |
| AVGO | Broadcom | Custom AI accelerators, networking |
| AMD | AMD | MI300 AI accelerators, EPYC |
| AAPL | Apple | On-device AI, Apple Intelligence |
| ORCL | Oracle | Cloud AI infrastructure |
| IBM | IBM | Watson, enterprise AI |
| PLTR | Palantir | AI/ML data platforms, AIP |
| NOW | ServiceNow | AI-powered workflow automation |
| SNOW | Snowflake | AI/ML data cloud |
| DDOG | Datadog | AI observability, LLM monitoring |
| CRM | Salesforce | Einstein AI, Agentforce |
| ADBE | Adobe | Firefly AI, generative tools |
| INTU | Intuit | AI-driven financial tools |
| CRWD | CrowdStrike | AI cybersecurity |
| AI | C3.ai | Enterprise AI software |

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

# Export results
python -m ai_watchlist export --format csv
python -m ai_watchlist export --format json

# Save analysis to file
python -m ai_watchlist analyze --save --output my_watchlist.json
```

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

### Z-Score Calculation

For each indicator, we calculate a Z-score using a rolling 4-week baseline:

```
Z = (Current Value - 4-Week Mean) / 4-Week Standard Deviation
Composite Score = Σ (Z-Score × Weight)
```

## Project Structure

```
ai_watchlist/
├── __init__.py           # Package exports
├── __main__.py           # CLI entry point
├── config.py             # Companies, weights, thresholds
├── models.py             # Data classes
├── watchlist.py          # Main AIWatchlist class
├── scoring.py            # Scoring engine
├── data/                 # Output directory
│   └── historical/       # Historical tracking
└── indicators/
    ├── __init__.py
    ├── sec.py            # SEC filings indicator
    ├── jobs.py           # Job postings indicator
    ├── github.py         # GitHub activity indicator
    ├── executives.py     # Executive appearances indicator
    ├── sentiment.py      # Employee sentiment indicator
    └── contracts.py      # Government contracts indicator
```

## API Usage

```python
import asyncio
from ai_watchlist import AIWatchlist

async def main():
    # Initialize watchlist
    watchlist = AIWatchlist(use_mock=True, use_cache=True)
    
    # Analyze all companies
    scores = await watchlist.analyze_all()
    
    # Get top companies
    for score in scores[:5]:
        print(f"{score.ticker}: {score.composite_score:.2f} - {score.signal.value}")
    
    # Analyze specific company
    from ai_watchlist.config import COMPANIES
    nvda = next(c for c in COMPANIES if c["ticker"] == "NVDA")
    score = await watchlist.analyze_company(nvda)
    watchlist.print_company_detail(score)
    
    # Save results
    watchlist.save_results(scores, "my_analysis.json")

asyncio.run(main())
```

## Real Data Integration

By default, the tool uses mock data for demonstration. To connect real data sources:

```python
watchlist = AIWatchlist(
    use_mock=False,           # Disable mock data
    use_cache=True,           # Enable caching
    github_token="your_token" # Optional: GitHub API token for higher rate limits
)
```

### Data Sources

| Indicator | Source | API |
|-----------|--------|-----|
| SEC Filings | SEC EDGAR | Free |
| GitHub Activity | GitHub API | Free tier available |
| Government Contracts | USAspending.gov | Free |
| Job Postings | LinkedIn, Indeed | Requires scraping/paid API |
| Employee Sentiment | Glassdoor | Paid API |
| Executive Appearances | Various | Requires aggregation |

## Configuration

Edit `ai_watchlist/config.py` to customize:

- Add/remove companies from the watchlist
- Adjust indicator weights
- Modify signal thresholds
- Add custom AI keywords

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

## Acknowledgments

- SEC EDGAR for filing data
- GitHub API for repository statistics
- USAspending.gov for government contract data

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history.
