#!/usr/bin/env python3
"""
Market data utility package.
Expose core helper dataclasses and high-level report builders.
"""

from .core import (  # noqa: F401
    MarketDataPoint,
    MultiPeriodMarketData,
    format_market_data_point,
    get_market_data_point,
    get_multi_period_data,
    get_market_status_emoji,
    is_market_open,
)
from .overview import (  # noqa: F401
    get_index_futures_overview,
    get_market_overview_with_periods,
)
from .stocks import get_stock_analysis_report  # noqa: F401
from .crypto import get_crypto_overview_report  # noqa: F401
from .sectors import get_sector_performance_report  # noqa: F401

__all__ = [
    "MarketDataPoint",
    "MultiPeriodMarketData",
    "format_market_data_point",
    "get_market_data_point",
    "get_multi_period_data",
    "get_market_status_emoji",
    "is_market_open",
    "get_index_futures_overview",
    "get_market_overview_with_periods",
    "get_stock_analysis_report",
    "get_crypto_overview_report",
    "get_sector_performance_report",
]
