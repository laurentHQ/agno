#!/usr/bin/env python3
"""
Backwards-compatible facade for market data utilities.

This module re-exports the split helpers located under src/utils/market_data/.
"""

from __future__ import annotations

from utils.market_data import (
    MarketDataPoint,
    MultiPeriodMarketData,
    format_market_data_point,
    get_crypto_overview_report,
    get_index_futures_overview,
    get_market_data_point,
    get_market_overview_with_periods,
    get_market_status_emoji,
    get_multi_period_data,
    get_sector_performance_report,
    get_stock_analysis_report,
    is_market_open,
)

__all__ = [
    "MarketDataPoint",
    "MultiPeriodMarketData",
    "format_market_data_point",
    "get_market_data_point",
    "get_multi_period_data",
    "get_market_overview_with_periods",
    "get_index_futures_overview",
    "get_stock_analysis_report",
    "get_crypto_overview_report",
    "get_sector_performance_report",
    "is_market_open",
    "get_market_status_emoji",
]
