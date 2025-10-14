
#!/usr/bin/env python3
"""Toolkit for finance news agent."""

from __future__ import annotations

import os

from agno.tools import Toolkit
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.reddit import RedditTools
from agno.tools.tavily import TavilyTools
from agno.tools.yfinance import YFinanceTools

from market_data_utils import (
    get_crypto_overview_report,
    get_index_futures_overview,
    get_market_overview_with_periods,
    get_sector_performance_report,
    get_stock_analysis_report,
)


class AdvancedFinanceTools(Toolkit):
    """Enhanced financial toolkit with market data, analysis, and news capabilities."""

    def __init__(self) -> None:
        super().__init__(name="advanced_finance_tools", auto_register=False)

        self.register(self.get_market_overview)
        self.register(self.get_stock_analysis)
        self.register(self.get_crypto_overview)
        self.register(self.get_sector_performance)
        self.register(self.get_index_futures_preview)

    def get_market_overview(
        self,
        include_daily: bool = True,
        include_wtd: bool = True,
        include_mtd: bool = True,
        include_ytd: bool = True,
        compact: bool = True,
        include_futures_preview: bool = True,
    ) -> str:
        """Return a market overview across indices and asset classes."""
        try:
            indices = {
                "S&P 500": "^GSPC",
                "Dow Jones": "^DJI",
                "NASDAQ": "^IXIC",
                "Russell 2000": "^RUT",
                "VIX": "^VIX",
                "Hang Seng (HSI)": "^HSI",
                "EURO STOXX 50": "^STOXX50E",
                "EUR/USD": "EURUSD=X",
                "US Dollar Index": "DX-Y.NYB",
                "Gold": "GC=F",
                "Crude Oil (WTI)": "CL=F",
            }

            return get_market_overview_with_periods(
                indices=indices,
                include_daily=include_daily,
                include_wtd=include_wtd,
                include_mtd=include_mtd,
                include_ytd=include_ytd,
                compact=compact,
                include_futures_preview=include_futures_preview,
            )
        except Exception as exc:  # noqa: BLE001
            return f"Error fetching market overview: {exc!s}"

    def get_index_futures_preview(
        self,
        include_daily: bool = True,
        include_wtd: bool = False,
        include_mtd: bool = False,
        include_ytd: bool = False,
        compact: bool = True,
    ) -> str:
        """Return equity index futures snapshot for pre-market sentiment."""
        try:
            return get_index_futures_overview(
                include_daily=include_daily,
                include_wtd=include_wtd,
                include_mtd=include_mtd,
                include_ytd=include_ytd,
                compact=compact,
            )
        except Exception as exc:  # noqa: BLE001
            return f"Error fetching index futures data: {exc!s}"

    def get_stock_analysis(self, symbol: str) -> str:
        """Return detailed stock analysis with fundamentals and performance."""
        return get_stock_analysis_report(symbol)

    def get_crypto_overview(self) -> str:
        """Return a formatted cryptocurrency market overview."""
        return get_crypto_overview_report()

    def get_sector_performance(self) -> str:
        """Return sector performance summary."""
        return get_sector_performance_report()


def build_optional_tools() -> list:
    """Return optional third-party tools depending on environment variables."""
    optional_tools: list = []

    if os.getenv("TAVILY_API_KEY"):
        optional_tools.append(
            TavilyTools(
                enable_search=True,
                search_depth="advanced",
                max_tokens=6000,
                include_answer=True,
                format="markdown",
            )
        )

    if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"):
        optional_tools.append(RedditTools())

    return optional_tools


def build_finance_tools() -> list:
    """Return the complete set of tools for the finance agent."""
    base_tools = [
        AdvancedFinanceTools(),
        YFinanceTools(),
        DuckDuckGoTools(enable_search=True, enable_news=True),
        HackerNewsTools(),
    ]
    return base_tools + build_optional_tools()
