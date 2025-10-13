#!/usr/bin/env python3
"""
Manual smoke test for finance utility report helpers.
Calls get_stock_analysis_report, get_crypto_overview_report,
and get_sector_performance_report and prints trimmed output.
"""

from pathlib import Path
import sys

# Ensure project modules are importable when running directly.
current_dir = Path(__file__).parent
repo_root = current_dir.parent
sys.path.insert(0, str(repo_root / "src" / "utils"))

from market_data_utils import (  # noqa: E402
    get_crypto_overview_report,
    get_sector_performance_report,
    get_stock_analysis_report,
)


def print_section(title: str, content: str, max_chars: int = 800) -> None:
    """Print a bannered section with optional truncation for readability."""
    print("=" * 80)
    print(title)
    print("=" * 80)

    if len(content) > max_chars:
        print(content[:max_chars])
        print("\n... (truncated)")
    else:
        print(content)


def main() -> None:
    """Execute report helpers and display their output."""
    stock_symbol = "AAPL"
    stock_report = get_stock_analysis_report(stock_symbol)
    print_section(f"Stock Analysis Report - {stock_symbol}", stock_report)

    crypto_report = get_crypto_overview_report()
    print_section("Cryptocurrency Overview Report", crypto_report)

    sector_report = get_sector_performance_report()
    print_section("Sector Performance Report", sector_report)

    print("\n✅ Finance report helper smoke test complete!")


if __name__ == "__main__":
    main()
