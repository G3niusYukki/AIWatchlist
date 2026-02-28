#!/usr/bin/env python3
"""
AI Company Watchlist - Command Line Interface
Track leading indicators for AI companies and generate buy/sell signals
"""

import argparse
import asyncio
import json
import os
import sys
from datetime import datetime

from ai_watchlist.watchlist import AIWatchlist
from ai_watchlist.config import COMPANIES


def create_parser():
    parser = argparse.ArgumentParser(
        description="AI Company Watchlist - Track leading indicators for AI stocks",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m ai_watchlist analyze                    # Analyze all companies
  python -m ai_watchlist analyze --top 10           # Show top 10
  python -m ai_watchlist analyze -t NVDA MSFT GOOGL # Analyze specific tickers
  python -m ai_watchlist detail NVDA                # Show detailed analysis
  python -m ai_watchlist history NVDA               # Show historical data
  python -m ai_watchlist list                       # List all tracked companies
  python -m ai_watchlist export --format json       # Export results
  python -m ai_watchlist dashboard                  # Launch web dashboard
  python -m ai_watchlist backtest NVDA --weeks 12   # Run backtest
  python -m ai_watchlist sectors                    # Sector comparison
  python -m ai_watchlist prices                     # Fetch price data
  python -m ai_watchlist data NVDA                  # Additional data sources
""",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    analyze_parser = subparsers.add_parser(
        "analyze", help="Analyze companies and generate signals"
    )
    analyze_parser.add_argument(
        "-t", "--tickers", nargs="+", help="Specific tickers to analyze"
    )
    analyze_parser.add_argument(
        "--top", type=int, default=20, help="Number of top companies to show"
    )
    analyze_parser.add_argument("--no-cache", action="store_true", help="Disable cache")
    analyze_parser.add_argument(
        "--save", action="store_true", help="Save results to file"
    )
    analyze_parser.add_argument("--output", "-o", help="Output filename")

    detail_parser = subparsers.add_parser(
        "detail", help="Show detailed analysis for a company"
    )
    detail_parser.add_argument("ticker", help="Ticker symbol")

    history_parser = subparsers.add_parser(
        "history", help="Show historical data for a company"
    )
    history_parser.add_argument("ticker", help="Ticker symbol")

    subparsers.add_parser("list", help="List all tracked companies")

    export_parser = subparsers.add_parser("export", help="Export results")
    export_parser.add_argument(
        "--format", choices=["json", "csv"], default="json", help="Export format"
    )
    export_parser.add_argument("--output", "-o", default=None, help="Output filename")

    dashboard_parser = subparsers.add_parser("dashboard", help="Launch web dashboard")
    dashboard_parser.add_argument("--host", default="0.0.0.0", help="Host to bind to")
    dashboard_parser.add_argument("--port", type=int, default=8000, help="Port to use")

    backtest_parser = subparsers.add_parser("backtest", help="Run backtesting")
    backtest_parser.add_argument("ticker", help="Ticker to backtest")
    backtest_parser.add_argument(
        "--weeks", type=int, default=12, help="Weeks to backtest"
    )
    backtest_parser.add_argument(
        "--capital", type=float, default=100000, help="Initial capital"
    )
    backtest_parser.add_argument(
        "--compare", action="store_true", help="Compare all strategies"
    )

    sectors_parser = subparsers.add_parser("sectors", help="Sector comparison analysis")
    sectors_parser.add_argument("--compare", nargs="+", help="Compare specific tickers")

    prices_parser = subparsers.add_parser("prices", help="Fetch price data")
    prices_parser.add_argument("-t", "--tickers", nargs="+", help="Specific tickers")

    data_parser = subparsers.add_parser("data", help="Additional data sources")
    data_parser.add_argument("ticker", help="Ticker symbol")

    return parser


async def run_analyze(args):
    watchlist = AIWatchlist(use_mock=True, use_cache=not args.no_cache)

    print(
        f"Analyzing {len(COMPANIES) if not args.tickers else len(args.tickers)} companies..."
    )

    scores = await watchlist.analyze_all(tickers=args.tickers)

    watchlist.print_report(scores, top_n=args.top)

    if args.save or args.output:
        path = watchlist.save_results(scores, filename=args.output)
        print(f"\nResults saved to: {path}")

    return scores


async def run_detail(args):
    watchlist = AIWatchlist(use_mock=True, use_cache=True)

    company = next((c for c in COMPANIES if c["ticker"] == args.ticker.upper()), None)
    if not company:
        print(f"Error: Company {args.ticker} not found in watchlist")
        sys.exit(1)

    score = await watchlist.analyze_company(company)
    watchlist.print_company_detail(score)

    return score


def run_history(args):
    watchlist = AIWatchlist(use_mock=True, use_cache=True)

    history = watchlist.get_company_history(args.ticker.upper())

    if not history:
        print(f"No historical data found for {args.ticker}")
        return

    print(f"\nHistorical Data for {args.ticker.upper()}")
    print("=" * 60)

    for indicator, entries in history.items():
        print(f"\n{indicator}:")
        for entry in entries[-8:]:
            print(f"  {entry['timestamp'][:10]}: {entry['value']:.3f}")

    report = watchlist.scoring_engine.get_weekly_report(args.ticker.upper())
    print("\n4-Week Summary:")
    print("-" * 40)
    for ind, data in report.get("indicators", {}).items():
        print(
            f"  {ind}: current={data['current']:.3f}, avg={data['4wk_avg']:.3f}, trend={data['trend']}"
        )


def run_list():
    from ai_watchlist.sectors import SECTOR_MAPPING

    print("\nTracked AI Companies")
    print("=" * 70)
    print(f"{'Ticker':>8} {'Company Name':<30} {'Sector':<25}")
    print("-" * 70)

    for company in COMPANIES:
        ticker = company["ticker"]
        name = company["name"]
        sector = SECTOR_MAPPING.get(ticker, "Other")
        print(f"{ticker:>8} {name:<30} {sector:<25}")


async def run_export(args):
    watchlist = AIWatchlist(use_mock=True, use_cache=True)

    scores = await watchlist.analyze_all()

    filename = (
        args.output
        or f"watchlist_export_{datetime.now().strftime('%Y%m%d')}.{args.format}"
    )

    if args.format == "json":
        path = watchlist.save_results(scores, filename)
    else:
        path = export_csv(scores, filename)

    print(f"Exported to: {path}")


def export_csv(scores, filename):
    import csv

    path = os.path.join(os.path.dirname(__file__), "data", filename)

    with open(path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow(
            [
                "rank",
                "ticker",
                "company_name",
                "composite_score",
                "signal",
                "sec_filings_z",
                "job_postings_z",
                "github_activity_z",
                "exec_appearances_z",
                "employee_sentiment_z",
                "govt_contracts_z",
            ]
        )

        for i, score in enumerate(scores):
            indicators = {s.indicator_name: s.z_score for s in score.indicator_scores}
            writer.writerow(
                [
                    i + 1,
                    score.ticker,
                    score.company_name,
                    round(score.composite_score, 3),
                    score.signal.value,
                    round(indicators.get("sec_filings", 0), 3),
                    round(indicators.get("job_postings", 0), 3),
                    round(indicators.get("github_activity", 0), 3),
                    round(indicators.get("exec_appearances", 0), 3),
                    round(indicators.get("employee_sentiment", 0), 3),
                    round(indicators.get("govt_contracts", 0), 3),
                ]
            )

    return path


def run_dashboard(args):
    from ai_watchlist.dashboard import run_dashboard

    print(f"\nStarting AI Watchlist Dashboard...")
    print(f"Open http://localhost:{args.port} in your browser\n")

    run_dashboard(host=args.host, port=args.port, use_mock=True)


async def run_backtest(args):
    from ai_watchlist.backtest import Backtester, BacktestStrategy

    backtester = Backtester(
        initial_capital=args.capital, strategy=BacktestStrategy.SIGNAL_FOLLOW
    )

    print(f"\nRunning backtest for {args.ticker.upper()}...")
    print(f"Period: {args.weeks} weeks | Initial Capital: ${args.capital:,.0f}")
    print("=" * 60)

    if args.compare:
        result = await backtester.compare_strategies(args.ticker.upper(), args.weeks)

        print("\nStrategy Comparison:")
        print("-" * 60)
        for strategy, metrics in result["strategy_comparison"].items():
            print(f"\n{strategy}:")
            print(f"  Return: {metrics['return_pct']:.2f}%")
            print(f"  Win Rate: {metrics['win_rate']:.1%}")
            print(f"  Sharpe: {metrics['sharpe']:.2f}")
            print(f"  Max Drawdown: {metrics['max_drawdown']:.2f}%")

        print(f"\nBest Strategy: {result['best_strategy']}")
    else:
        result = await backtester.run_backtest(args.ticker.upper(), args.weeks)

        print(f"\nResults:")
        print(f"  Final Capital: ${result['final_capital']:,.2f}")
        print(f"  Total Return: {result['total_return_pct']:.2f}%")
        print(f"  Benchmark Return: {result['benchmark_return_pct']:.2f}%")
        print(f"  Alpha: {result['alpha']:.2f}%")
        print(f"\nTrade Statistics:")
        print(f"  Total Trades: {result['total_trades']}")
        print(
            f"  Winning: {result['winning_trades']} | Losing: {result['losing_trades']}"
        )
        print(f"  Win Rate: {result['win_rate']:.1%}")
        print(
            f"  Avg Win: {result['avg_win_pct']:.2f}% | Avg Loss: {result['avg_loss_pct']:.2f}%"
        )
        print(f"\nRisk Metrics:")
        print(f"  Max Drawdown: {result['max_drawdown']:.2f}%")
        print(f"  Sharpe Ratio: {result['sharpe_ratio']:.2f}")


async def run_sectors(args):
    from ai_watchlist.sectors import SectorAnalyzer

    analyzer = SectorAnalyzer(use_mock=True)

    if args.compare:
        result = await analyzer.compare_companies(args.compare)

        print("\nCompany Comparison")
        print("=" * 70)

        for company in result["companies"]:
            print(f"\n{company['ticker']} - {company['name']}")
            print(f"  Score: {company['score']:.3f} | Signal: {company['signal']}")

        if result["winner"]:
            w = result["winner"]
            print(
                f"\nWinner: {w['ticker']} (Score: {w['score']}, Signal: {w['signal']})"
            )
    else:
        result = await analyzer.analyze_sectors()

        print("\nSector Analysis")
        print("=" * 70)
        print(f"Generated: {result['generated_at']}")

        print("\nSector Rankings (by avg score):")
        print("-" * 70)
        for sector in result["rankings"]["by_sector_score"]:
            data = result["sectors"][sector]
            print(f"\n{sector}:")
            print(f"  Avg Score: {data['avg_score']:.3f}")
            print(f"  Signal: {data['avg_signal']}")
            print(f"  Companies: {data['company_count']}")
            print(
                f"  Top: {data['top_performer']} | Bottom: {data['bottom_performer']}"
            )

        print("\n" + "=" * 70)
        print("Sector Rotation Signal:")
        rotation = result["sector_rotation"]
        print(f"  Recommendation: {rotation['recommendation']}")
        print(f"  Reasoning: {rotation['reasoning']}")

        print("\nTop Picks:")
        for pick in result["top_picks"]:
            print(f"  {pick['ticker']} ({pick['sector']}): {pick['reason']}")


async def run_prices(args):
    from ai_watchlist.indicators.prices import PriceIntegrator
    from ai_watchlist.config import COMPANIES

    integrator = PriceIntegrator(use_cache=True)

    tickers = args.tickers if args.tickers else [c["ticker"] for c in COMPANIES]

    print(f"\nFetching prices for {len(tickers)} companies...")
    print("=" * 90)
    print(
        f"{'Ticker':>8} {'Price':>10} {'Day%':>8} {'Week%':>8} {'Month%':>8} {'>50MA':>6} {'>200MA':>6}"
    )
    print("-" * 90)

    for ticker in tickers:
        price = await integrator.fetch_price(ticker)
        print(
            f"{price.ticker:>8} "
            f"${price.current_price:>8.2f} "
            f"{price.day_change_pct:>7.2f}% "
            f"{price.week_change_pct:>7.2f}% "
            f"{price.month_change_pct:>7.2f}% "
            f"{'✓' if price.above_50dma else '✗':>6} "
            f"{'✓' if price.above_200dma else '✗':>6}"
        )


async def run_data(args):
    from ai_watchlist.indicators.data_sources import DataIntegrator
    from ai_watchlist.config import COMPANIES

    ticker = args.ticker.upper()
    company = next((c for c in COMPANIES if c["ticker"] == ticker), None)

    if not company:
        print(f"Company {ticker} not found")
        return

    integrator = DataIntegrator(use_mock=True)

    print(f"\nFetching additional data for {ticker}...")
    print("=" * 70)

    data = await integrator.fetch_all(ticker, company["name"])

    print(f"\nNews ({data['news']['article_count']} articles)")
    print(f"  Sentiment Score: {data['news']['sentiment_score']:.3f}")
    for article in data["news"]["articles"][:3]:
        print(f"  - [{article['source']}] {article['title'][:50]}...")

    print(f"\nEarnings")
    if data["earnings"]["quarter"]:
        print(f"  Quarter: {data['earnings']['quarter']}")
        print(f"  Surprise: {data['earnings']['surprise_pct']:.2f}%")
        print(f"  AI Mentions in Call: {data['earnings']['ai_mentions']}")
    else:
        print("  No recent earnings data")

    print(f"\nSocial Sentiment")
    print(f"  Aggregate: {data['social']['aggregate_sentiment']:.3f}")
    for platform in data["social"]["platforms"]:
        print(
            f"  - {platform['name']}: {platform['mentions']} mentions, sentiment {platform['sentiment']:.2f}"
        )

    print(f"\nPatents")
    print(f"  AI Patents (4wk): {data['patents']['ai_patents']}")
    print(f"  Innovation Score: {data['patents']['innovation_score']:.2f}")

    print(f"\nAnalyst Ratings")
    print(f"  Consensus: {data['analysts']['consensus']}")
    print(f"  Avg Target: ${data['analysts']['avg_target']:.2f}")
    print(f"  Buy Ratio: {data['analysts']['buy_ratio']:.0%}")


async def main():
    parser = create_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(0)

    if args.command == "analyze":
        await run_analyze(args)
    elif args.command == "detail":
        await run_detail(args)
    elif args.command == "history":
        run_history(args)
    elif args.command == "list":
        run_list()
    elif args.command == "export":
        await run_export(args)
    elif args.command == "dashboard":
        run_dashboard(args)
    elif args.command == "backtest":
        await run_backtest(args)
    elif args.command == "sectors":
        await run_sectors(args)
    elif args.command == "prices":
        await run_prices(args)
    elif args.command == "data":
        await run_data(args)


if __name__ == "__main__":
    asyncio.run(main())
