#!/usr/bin/env python3
"""
Sector performance reporting helper.
"""

from __future__ import annotations

from datetime import datetime

import yfinance as yf

from .core import compute_equity_ttl, get_cached_result, is_market_open, set_cached_result

__all__ = ["get_sector_performance_report"]


def get_sector_performance_report() -> str:
    """
    Generate sector performance overview using major sector ETFs with caching.
    """
    _, market_status = is_market_open()
    cache_key = ("sector_performance", market_status)
    cached_result = get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    sectors = {
        "Technology": "XLK",
        "Healthcare": "XLV",
        "Financials": "XLF",
        "Energy": "XLE",
        "Consumer Discretionary": "XLY",
        "Industrials": "XLI",
        "Consumer Staples": "XLP",
        "Materials": "XLB",
        "Real Estate": "XLRE",
        "Utilities": "XLU",
        "Communications": "XLC",
    }

    try:
        sector_results: list[tuple[str, str, float]] = []
        for sector, etf in sectors.items():
            ticker = yf.Ticker(etf)
            hist = ticker.history(period="5d")
            if hist.empty or len(hist) <= 1:
                raise ValueError(f"Insufficient data for {sector} sector ({etf})")

            current_price = hist["Close"].iloc[-1]
            prev_price = hist["Close"].iloc[0]
            if prev_price == 0:
                raise ValueError(f"Invalid previous price for {sector} sector ({etf})")

            change_pct = (current_price / prev_price - 1) * 100
            sector_results.append((sector, etf, change_pct))

        sector_results.sort(key=lambda item: item[2], reverse=True)
        report_lines = [f"## Sector Performance - {datetime.now().strftime('%Y-%m-%d')}\n"]
        report_lines.append("### 5-Day Sector Performance (Best to Worst)\n")

        for sector, etf, change in sector_results:
            direction = "📈" if change >= 0 else "📉"
            report_lines.append(f"{direction} **{sector}** ({etf}): {change:+.2f}%")

        result = "\n".join(report_lines)
    except Exception as exc:  # noqa: BLE001
        result = f"Error fetching sector performance: {exc!s}"

    ttl = compute_equity_ttl(market_status)
    return set_cached_result(cache_key, result, ttl)
