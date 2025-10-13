#!/usr/bin/env python3
"""
Quick smoke test for get_crypto_overview_report utility.
Fetches the report and prints the first section for inspection.
"""

from pathlib import Path
import sys

current_dir = Path(__file__).parent
repo_root = current_dir.parent
sys.path.insert(0, str(repo_root / "src" / "utils"))

from market_data_utils import get_crypto_overview_report  # noqa: E402


def test_get_crypto_overview() -> None:
    """Fetch crypto overview and print a snippet for manual verification."""
    report = get_crypto_overview_report()
    print("=" * 80)
    print("Crypto Overview Report")
    print("=" * 80)
    print(report[:1000])
    if len(report) > 1000:
        print("\n... (truncated)")


if __name__ == "__main__":
    test_get_crypto_overview()
