"""auto-daily: macOS window context capture and daily report generator."""

__version__ = "0.1.0"

from auto_daily.cli import create_parser
from auto_daily.config import load_env
from auto_daily.monitor import start_monitoring
from auto_daily.report import run_report_command, run_summarize_command


def main() -> None:
    """Main entry point for auto-daily."""
    load_env()

    parser = create_parser(__version__)
    args = parser.parse_args()

    if args.command == "report":
        run_report_command(args.date, args.with_calendar, args.auto_summarize)
    elif args.command == "summarize":
        run_summarize_command(args.date, args.hour)
    elif args.start:
        start_monitoring(__version__)
    else:
        print(f"auto-daily v{__version__}")
