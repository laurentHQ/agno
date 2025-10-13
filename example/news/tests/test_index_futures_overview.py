#!/usr/bin/env python3
"""
Utility script to preview index futures snapshots from the finance toolkit.
Demonstrates both markdown (compact) and JSON outputs of get_index_futures_overview.
"""

import json
from pathlib import Path
import sys

# Ensure project modules are discoverable when running directly
current_dir = Path(__file__).parent
repo_root = current_dir.parent
sys.path.insert(0, str(repo_root / "src" / "utils"))
sys.path.insert(0, str(repo_root / "src" / "agents"))

from finance_news_agent import AdvancedFinanceTools  # noqa: E402
from market_data_utils import get_index_futures_overview  # noqa: E402


def main() -> None:
    """Display index futures overview via both the toolkit and utility helper."""
    tools = AdvancedFinanceTools()

    print("=" * 80)
    print("Index Futures Overview Preview")
    print("=" * 80)

    # Tool usage (markdown)
    print("\n1. AdvancedFinanceTools.get_index_futures_preview (compact=True)")
    print("-" * 80)
    markdown_result = tools.get_index_futures_preview(compact=True)
    print(markdown_result)

    # Tool usage (JSON)
    print("\n2. AdvancedFinanceTools.get_index_futures_preview (compact=False)")
    print("-" * 80)
    json_result = tools.get_index_futures_preview(compact=False)
    try:
        parsed = json.loads(json_result)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as error:
        print(f"❌ Failed to parse JSON output: {error}")
        print(json_result)

    # Direct utility usage to demonstrate identical payload
    print("\n3. Direct market_data_utils.get_index_futures_overview (compact=False)")
    print("-" * 80)
    util_json = get_index_futures_overview(compact=False)
    try:
        parsed = json.loads(util_json)
        print(json.dumps(parsed, indent=2))
    except json.JSONDecodeError as error:
        print(f"❌ Failed to parse JSON output from utility: {error}")
        print(util_json)

    print("\n" + "=" * 80)
    print("✅ Futures preview test complete!")
    print("=" * 80)


if __name__ == "__main__":
    main()
