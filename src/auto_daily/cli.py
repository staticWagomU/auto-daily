"""CLI argument parser for auto-daily."""

import argparse


def create_parser(version: str) -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser.

    Args:
        version: Version string to display with --version flag.

    Returns:
        Configured ArgumentParser instance.
    """
    parser = argparse.ArgumentParser(
        prog="auto-daily",
        description="macOS window context capture and daily report generator",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {version}",
    )

    subparsers = parser.add_subparsers(dest="command")

    # Start command (legacy --start flag support)
    parser.add_argument(
        "--start",
        action="store_true",
        help="Start window monitoring",
    )

    # Report subcommand
    report_parser = subparsers.add_parser(
        "report",
        help="Generate a daily report from logs",
    )
    report_parser.add_argument(
        "--date",
        type=str,
        help="Date to generate report for (YYYY-MM-DD format)",
    )
    report_parser.add_argument(
        "--with-calendar",
        action="store_true",
        help="Include calendar events in the report",
    )
    report_parser.add_argument(
        "--auto-summarize",
        action="store_true",
        help="Automatically generate missing summaries before report",
    )

    # Summarize subcommand
    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Generate an hourly summary from logs",
    )
    summarize_parser.add_argument(
        "--date",
        type=str,
        help="Date to summarize (YYYY-MM-DD format)",
    )
    summarize_parser.add_argument(
        "--hour",
        type=int,
        help="Hour to summarize (0-23)",
    )

    return parser
