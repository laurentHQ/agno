#!/usr/bin/env python3
"""
Test script to demonstrate improved stock quote display with delta and colors
Tests the enhanced YFinanceTools with delta from previous day and color indicators
"""
import os
from pathlib import Path
import sys

# Add paths for imports from organized structure
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(news_root / "src"))

from dotenv import load_dotenv
from agno.tools.yfinance import YFinanceTools
from utils.market_data import get_stock_analysis_report

# Load environment variables
load_dotenv()

def test_stock_display():
    """Test the enhanced stock display with delta and colors"""

    # Create the YFinanceTools instance
    tools = YFinanceTools()

    # Test symbols
    symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]

    print("=" * 80)
    print("Enhanced Stock Quote Display - Testing Delta and Color Indicators")
    print("=" * 80)
    print()

    # Test get_current_stock_price
    print("### Testing get_current_stock_price() ###")
    print()
    for symbol in symbols:
        print(f"Testing {symbol}:")
        result = tools.get_current_stock_price(symbol)
        print(result)
        print()

    print("=" * 80)
    print()

    # Test get_company_info (shows price in JSON)
    print("### Testing get_company_info() for AAPL ###")
    print()
    result = tools.get_company_info("AAPL")
    print(result)
    print()

    print("=" * 80)
    print()

    # Test get_stock_fundamentals (shows price in JSON)
    print("### Testing get_stock_fundamentals() for MSFT ###")
    print()
    result = tools.get_stock_fundamentals("MSFT")
    print(result)
    print()

    print("=" * 80)
    print()

    # Test stock analysis report with pre-market data
    print("### Testing get_stock_analysis_report() with pre-market snapshot ###")
    print()
    for symbol in ["AAPL", "MSFT"]:
        print(f"Report for {symbol}:")
        report = get_stock_analysis_report(symbol)
        # Print only the top portion to highlight pre-market section
        head, _, _ = report.partition("### Key Metrics")
        print(head + "### Key Metrics")
        print("...")
        print()

    print("=" * 80)
    print("Test completed!")
    print("=" * 80)

if __name__ == "__main__":
    test_stock_display()
