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
    print("\nTracked AI Companies")
    print("=" * 60)
    print(f"{'Ticker':>8} {'Company Name':<40} {'Primary AI Focus':<30}")
    print("-" * 60)

    for company in COMPANIES:
        ticker = company["ticker"]
        name = company["name"]
        print(f"{ticker:>8} {name:<40}")


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


if __name__ == "__main__":
    asyncio.run(main())
