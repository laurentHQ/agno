#!/usr/bin/env python3
"""
Test script for get_market_overview output
Tests the market overview function with JSON format output
"""

import json
from pathlib import Path
import sys

# Add paths for imports
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root / "src" / "utils"))
sys.path.insert(0, str(news_root / "src" / "agents"))

from finance_news_agent import AdvancedFinanceTools

def main():
    """Test the get_market_overview function with JSON and markdown table outputs"""
    # Create the tools instance
    tools = AdvancedFinanceTools()

    print("=" * 80)
    print("Testing get_market_overview - JSON and Markdown Table Formats")
    print("=" * 80)

    # Test 1: JSON format (default, compact=False)
    print("\n\n1. Testing JSON format (compact=False, all periods):")
    print("-" * 80)
    result = tools.get_market_overview(compact=False)

    # Parse and pretty-print JSON
    try:
        data = json.loads(result)
        # Show just first 2 indices to keep output manageable
        sample_data = {
            "timestamp": data["timestamp_formatted"],
            "market_status": data["market_status"],
            "indices": data["indices"][:2]
        }
        print(json.dumps(sample_data, indent=2))

        # Display summary
        print("\n📊 Summary:")
        print(f"   Format: JSON")
        print(f"   Market Status: {data['market_status']['status_text']}")
        print(f"   Timestamp: {data['timestamp_formatted']}")
        print(f"   Total Indices: {len(data['indices'])}")
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        print(result)

    # Test 2: Markdown table format (compact=True)
    print("\n\n2. Testing Markdown Table format (compact=True, all periods):")
    print("-" * 80)
    result = tools.get_market_overview(compact=True)
    print(result)

    # Test 3: Markdown table with only daily data
    print("\n\n3. Testing Markdown Table with only daily data:")
    print("-" * 80)
    result = tools.get_market_overview(
        include_daily=True,
        include_wtd=False,
        include_mtd=False,
        include_ytd=False,
        compact=True
    )
    print(result)

    # Test 4: Markdown table with selected periods
    print("\n\n4. Testing Markdown Table with Daily and YTD only:")
    print("-" * 80)
    result = tools.get_market_overview(
        include_daily=True,
        include_wtd=False,
        include_mtd=False,
        include_ytd=True,
        compact=True
    )
    print(result)

    print("\n" + "=" * 80)
    print("✅ Test complete!")
    print("📊 JSON format: compact=False (default)")
    print("📋 Markdown table format: compact=True")
    print("=" * 80)


if __name__ == "__main__":
    main()
