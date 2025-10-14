#!/usr/bin/env python3
"""
Stock analysis reporting helpers.
"""

from __future__ import annotations

from datetime import datetime, timezone
from zoneinfo import ZoneInfo

import yfinance as yf

from .core import (
    compute_equity_ttl,
    get_cached_result,
    is_market_open,
    set_cached_result,
    _build_premarket_section,
    _build_postmarket_section,
    _format_percent,
)

__all__ = ["get_stock_analysis_report"]


def get_stock_analysis_report(symbol: str) -> str:
    """
    Generate detailed stock analysis including fundamentals and recent performance.
    Applies caching to limit repeated calls to yfinance within a short window.
    """
    symbol_upper = symbol.upper()
    _, market_status = is_market_open()
    cache_key = ("stock_analysis", symbol_upper, market_status)
    cached_result = get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        ticker = yf.Ticker(symbol_upper)
        info = ticker.info
        hist = ticker.history(period="1mo")

        if hist.empty:
            result = f"No data available for symbol: {symbol}"
            ttl = 180
            return set_cached_result(cache_key, result, ttl)

        current_price = hist["Close"].iloc[-1]
        prev_close = info.get("previousClose")
        if not isinstance(prev_close, (int, float)):
            prev_close = current_price
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100 if prev_close else 0.0
        direction = "📈" if change >= 0 else "📉"

        lines = [
            f"## Stock Analysis: {info.get('longName', symbol_upper)} ({symbol_upper})",
            "",
            "### Current Price",
            f"{direction} **${current_price:.2f}** ({change:+.2f}, {change_pct:+.2f}%)",
        ]

        as_of_text: str | None = None
        market_time = info.get("regularMarketTime")
        if isinstance(market_time, (int, float)) and market_time > 0:
            et_tz = ZoneInfo("America/New_York")
            as_of_dt = datetime.fromtimestamp(market_time, tz=timezone.utc).astimezone(et_tz)
            as_of_text = as_of_dt.strftime("%Y-%m-%d %H:%M %Z")
        else:
            last_index = hist.index[-1]
            last_dt = None
            try:
                if hasattr(last_index, "to_pydatetime"):
                    last_dt = last_index.to_pydatetime()
                elif isinstance(last_index, datetime):
                    last_dt = last_index
            except Exception:
                last_dt = None

            if last_dt:
                if last_dt.tzinfo is None:
                    last_dt = last_dt.replace(tzinfo=timezone.utc)
                as_of_text = (
                    last_dt.astimezone(ZoneInfo("America/New_York")).strftime("%Y-%m-%d %H:%M %Z")
                )
            else:
                as_of_text = str(last_index)

        if as_of_text:
            lines.append(f"**As of**: {as_of_text}")

        pre_market_section = _build_premarket_section(info=info, ticker=ticker, previous_close=prev_close)
        post_market_section = _build_postmarket_section(info=info, ticker=ticker, previous_close=prev_close)

        if pre_market_section:
            lines.extend(["", *pre_market_section])
        if post_market_section:
            lines.extend(["", *post_market_section])

        lines.extend(["", "### Key Metrics"])

        market_cap = info.get("marketCap")
        if isinstance(market_cap, (int, float)):
            lines.append(f"- **Market Cap**: ${market_cap:,}")

        trailing_pe = info.get("trailingPE")
        if isinstance(trailing_pe, (int, float)):
            lines.append(f"- **P/E Ratio**: {trailing_pe}")

        high_52 = info.get("fiftyTwoWeekHigh")
        if isinstance(high_52, (int, float)):
            lines.append(f"- **52 Week High**: ${high_52}")

        low_52 = info.get("fiftyTwoWeekLow")
        if isinstance(low_52, (int, float)):
            lines.append(f"- **52 Week Low**: ${low_52}")

        volume = info.get("volume")
        if isinstance(volume, (int, float)):
            lines.append(f"- **Volume**: {int(volume):,}")

        dividend_yield = info.get("dividendYield")
        dividend_rate = info.get("trailingAnnualDividendRate")
        computed_yield = None
        if isinstance(dividend_rate, (int, float)) and dividend_rate and current_price:
            computed_yield = dividend_rate / current_price

        if isinstance(dividend_yield, (int, float)):
            base_yield = dividend_yield
            if computed_yield is not None and abs(base_yield - computed_yield) > 0.05:
                base_yield = computed_yield
            lines.append(f"- **Dividend Yield**: {_format_percent(base_yield)}")
        elif computed_yield is not None:
            lines.append(f"- **Dividend Yield**: {_format_percent(computed_yield)}")

        eps_trailing = info.get("trailingEps")
        if isinstance(eps_trailing, (int, float)):
            lines.append(f"- **Trailing EPS**: ${eps_trailing:.2f}")

        eps_forward = info.get("forwardEps")
        if isinstance(eps_forward, (int, float)):
            lines.append(f"- **Forward EPS**: ${eps_forward:.2f}")

        forward_pe = info.get("forwardPE")
        if isinstance(forward_pe, (int, float)):
            lines.append(f"- **Forward P/E**: {forward_pe:.2f}")

        forward_yield = info.get("fiveYearAvgDividendYield")
        if isinstance(forward_yield, (int, float)):
            if abs(forward_yield) > 0.2:
                forward_yield = forward_yield / 100
            lines.append(f"- **5Y Avg Dividend Yield**: {_format_percent(forward_yield)}")

        recommendation = info.get("recommendationKey")
        if isinstance(recommendation, str):
            lines.append(f"- **Analyst Rating**: {recommendation.title()}")

        summary = info.get("longBusinessSummary")
        if isinstance(summary, str) and summary:
            trimmed_summary = summary[:300] + "..." if len(summary) > 300 else summary
            lines.extend(["", "### Business Overview", trimmed_summary])

        lines.extend(["", "### Performance"])
        periods = {
            "1d": "1 day",
            "5d": "5 days",
            "1mo": "1 month",
            "3mo": "3 months",
            "6mo": "6 months",
            "ytd": "Year to Date",
            "1y": "1 year",
            "5y": "5 years",
        }

        for period, name in periods.items():
            try:
                period_hist = ticker.history(period=period)
                if not period_hist.empty and len(period_hist) > 1:
                    base_price = period_hist["Close"].iloc[0]
                    if base_price:
                        period_change = (period_hist["Close"].iloc[-1] / base_price - 1) * 100
                        lines.append(f"- **{name}**: {period_change:+.2f}%")
            except Exception as err:  # noqa: BLE001
                lines.append(f"- **{name}**: Error fetching data ({err!s})")

        result = "\n".join(lines)
    except Exception as exc:  # noqa: BLE001
        result = f"Error analyzing stock {symbol}: {exc!s}"

    ttl = compute_equity_ttl(market_status)
    return set_cached_result(cache_key, result, ttl)
