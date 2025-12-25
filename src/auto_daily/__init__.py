"""auto-daily: macOS window context capture and daily report generator."""

import argparse

__version__ = "0.1.0"


def main() -> None:
    """Main entry point for auto-daily."""
    parser = argparse.ArgumentParser(
        prog="auto-daily",
        description="macOS window context capture and daily report generator",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    parser.parse_args()

    print(f"auto-daily v{__version__}")
