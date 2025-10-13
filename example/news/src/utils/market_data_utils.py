#!/usr/bin/env python3
"""
Market Data Utilities
Helper functions for fetching and formatting market data with multiple time periods
"""

import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, NamedTuple
from zoneinfo import ZoneInfo

import requests
import yfinance as yf


class _CacheEntry(NamedTuple):
    value: Any
    expires_at: datetime


_CACHE: dict[str, _CacheEntry] = {}

_DEBUG_MODE_ENABLED = os.getenv("DEBUG_MODE", "").lower() in {"1", "true", "yes", "on"}
_CACHE_DEBUG_ENABLED = os.getenv("AGNO_CACHE_DEBUG")
if _CACHE_DEBUG_ENABLED is None:
    _CACHE_DEBUG_ENABLED = _DEBUG_MODE_ENABLED
else:
    _CACHE_DEBUG_ENABLED = _CACHE_DEBUG_ENABLED != "0"


def _cache_debug(message: str) -> None:
    """Emit cache debug messages when enabled."""
    if _CACHE_DEBUG_ENABLED:
        print(f"[cache] {message}")


def _shorten_key(key: str, max_length: int = 120) -> str:
    """Shorten cache key strings for debug readability."""
    if len(key) <= max_length:
        return key
    return key[: max_length - 3] + "..."


def _now_utc() -> datetime:
    """Return timezone-aware UTC timestamp."""
    return datetime.now(timezone.utc)


def _get_cache(key: str) -> Any | None:
    """Fetch cached value if it has not expired."""
    display_key = _shorten_key(key)
    entry = _CACHE.get(key)
    if not entry:
        _cache_debug(f"MISS {display_key} (fetching fresh data)")
        return None
    if entry.expires_at > _now_utc():
        _cache_debug(f"HIT {display_key} (serving cached result)")
        return entry.value
    _cache_debug(f"EXPIRED {display_key} (refreshing)")
    _CACHE.pop(key, None)
    return None


def _set_cache(key: str, value: Any, ttl_seconds: int) -> Any:
    """Store value in cache with a time-to-live."""
    expires_at = _now_utc() + timedelta(seconds=max(ttl_seconds, 1))
    _CACHE[key] = _CacheEntry(value=value, expires_at=expires_at)
    display_key = _shorten_key(key)
    _cache_debug(f"STORE {display_key} (cached for {ttl_seconds}s)")
    return value


def _format_percent(value: float) -> str:
    """Format numeric value as percentage, correcting for plain percent inputs."""
    if value is None:
        return "N/A"
    percent_value = value / 100 if abs(value) >= 1 else value
    return f"{percent_value:.2%}"


def _build_market_data_point_from_previous_close(
    ticker: yf.Ticker, name: str, symbol: str, period_label: str
) -> "MarketDataPoint | None":
    """
    Build a MarketDataPoint using regularMarketPrice and regularMarketPreviousClose
    when historical data is insufficient. Applies only to Daily period.
    """
    if period_label != "Daily":
        return None

    last_price: float | None = None
    previous_close: float | None = None

    try:
        info = ticker.info
    except Exception:
        info = {}

    if isinstance(info, dict):
        last_val = info.get("regularMarketPrice")
        prev_val = info.get("regularMarketPreviousClose")
        if isinstance(last_val, (int, float)):
            last_price = float(last_val)
        if isinstance(prev_val, (int, float)):
            previous_close = float(prev_val)

    if (last_price is None or previous_close is None) and hasattr(ticker, "fast_info"):
        fast_info = getattr(ticker, "fast_info", None)
        if fast_info is not None:
            if last_price is None:
                fi_last = getattr(fast_info, "last_price", None)
                if isinstance(fi_last, (int, float)):
                    last_price = float(fi_last)
            if previous_close is None:
                fi_prev = getattr(fast_info, "previous_close", None)
                if isinstance(fi_prev, (int, float)):
                    previous_close = float(fi_prev)

    if last_price is None or previous_close is None or previous_close == 0:
        return None

    change = last_price - previous_close
    change_pct = (change / previous_close) * 100 if previous_close else 0.0

    return MarketDataPoint(
        name=name,
        symbol=symbol,
        current_price=last_price,
        change=change,
        change_pct=change_pct,
        period=period_label,
        timestamp=datetime.now(),
        previous_close=previous_close,
    )


def _compute_market_ttl(status: str) -> int:
    """Determine cache TTL based on market status for timely refresh."""
    if status == "OPEN":
        return 60
    if status in {"PRE_MARKET", "AFTER_HOURS"}:
        return 180
    return 600


def _compute_equity_ttl(status: str) -> int:
    """TTL tuning for single-stock or sector snapshots."""
    if status == "OPEN":
        return 120
    if status in {"PRE_MARKET", "AFTER_HOURS"}:
        return 300
    return 600


def _set_cached_result(cache_key: tuple[Any, ...], value: Any, ttl_seconds: int) -> Any:
    """Helper to persist cached results using tuple-based key."""
    key_str = repr(cache_key)
    return _set_cache(key_str, value, ttl_seconds)


def _get_cached_result(cache_key: tuple[Any, ...]) -> Any | None:
    """Helper to retrieve tuple keyed cache entries."""
    key_str = repr(cache_key)
    return _get_cache(key_str)

# Equity index futures contracts used for pre-market insight
INDEX_FUTURES: dict[str, str] = {
    "S&P 500 Futures": "ES=F",
    "Dow Futures": "YM=F",
    "Nasdaq 100 Futures": "NQ=F",
    "Russell 2000 Futures": "RTY=F",
}


def is_market_open(market: str = "US") -> tuple[bool, str]:
    """
    Check if the market is currently open

    Args:
        market: Market to check ("US" for NYSE/NASDAQ)

    Returns:
        Tuple of (is_open: bool, status: str) where status is:
        - "OPEN" - Market is currently trading
        - "CLOSED" - Market is closed (after hours or weekend)
        - "PRE_MARKET" - Pre-market hours (4 AM - 9:30 AM ET)
        - "AFTER_HOURS" - After-hours trading (4 PM - 8 PM ET)
    """
    try:
        # Get current time in Eastern Time (US market timezone)
        et_tz = ZoneInfo("America/New_York")
        now_et = datetime.now(et_tz)

        # Check if weekend
        if now_et.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False, "CLOSED"

        current_time = now_et.time()

        # Market hours (all times in ET)
        pre_market_open = datetime.strptime("04:00", "%H:%M").time()
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        after_hours_close = datetime.strptime("20:00", "%H:%M").time()

        if market_open <= current_time < market_close:
            return True, "OPEN"
        elif pre_market_open <= current_time < market_open:
            return False, "PRE_MARKET"
        elif market_close <= current_time < after_hours_close:
            return False, "AFTER_HOURS"
        else:
            return False, "CLOSED"

    except Exception:
        # If timezone detection fails, return unknown status
        return False, "CLOSED"


def get_market_status_emoji(status: str) -> str:
    """Get emoji indicator for market status"""
    status_map = {
        "OPEN": "🔔",
        "CLOSED": "🔕",
        "PRE_MARKET": "🌅",
        "AFTER_HOURS": "🌙",
    }
    return status_map.get(status, "❓")


@dataclass
class MarketDataPoint:
    """Represents market data for a specific time period"""

    name: str
    symbol: str
    current_price: float
    change: float
    change_pct: float
    period: str
    timestamp: datetime
    error: str | None = None
    previous_close: float | None = None


@dataclass
class MultiPeriodMarketData:
    """Market data across multiple time periods"""

    name: str
    symbol: str
    current_price: float
    daily: MarketDataPoint | None = None
    wtd: MarketDataPoint | None = None  # Week-to-date
    mtd: MarketDataPoint | None = None  # Month-to-date
    ytd: MarketDataPoint | None = None  # Year-to-date
    market_status: str = "CLOSED"  # Market status: OPEN, CLOSED, PRE_MARKET, AFTER_HOURS
    error: str | None = None


def get_market_data_point(
    symbol: str,
    name: str,
    period: Literal["1d", "2d", "5d", "1mo", "1y"],
    period_label: str,
) -> MarketDataPoint | None:
    """
    Get market data for a specific symbol and time period

    Args:
        symbol: Ticker symbol (e.g., '^GSPC', 'AAPL')
        name: Display name for the symbol
        period: Time period for historical data ('1d', '2d', '5d', '1mo', '1y')
        period_label: Human-readable label ('Daily', 'WTD', 'MTD', 'YTD')

    Returns:
        MarketDataPoint with price and change data, or None if error
    """
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period=period)

        if hist.empty or len(hist) < 2:
            fallback_point = _build_market_data_point_from_previous_close(
                ticker=ticker,
                name=name,
                symbol=symbol,
                period_label=period_label,
            )
            if fallback_point is not None:
                return fallback_point
            return MarketDataPoint(
                name=name,
                symbol=symbol,
                current_price=0.0,
                change=0.0,
                change_pct=0.0,
                period=period_label,
                timestamp=datetime.now(),
                error=f"Insufficient data for {period_label}",
            )

        current_price = hist["Close"].iloc[-1]

        # For daily change, compare to previous day's close (second to last)
        # For other periods, compare to the start of the period
        previous_close = None
        if period_label == "Daily":
            previous_close = hist["Close"].iloc[-2] if len(hist) >= 2 else hist["Close"].iloc[0]
            start_price = previous_close
        else:
            start_price = hist["Close"].iloc[0]

        change = current_price - start_price
        change_pct = (change / start_price) * 100 if start_price != 0 else 0.0

        return MarketDataPoint(
            name=name,
            symbol=symbol,
            current_price=current_price,
            change=change,
            change_pct=change_pct,
            period=period_label,
            timestamp=datetime.now(),
            previous_close=previous_close,
        )

    except Exception as e:
        return MarketDataPoint(
            name=name,
            symbol=symbol,
            current_price=0.0,
            change=0.0,
            change_pct=0.0,
            period=period_label,
            timestamp=datetime.now(),
            error=str(e),
        )


def get_multi_period_data(
    symbol: str,
    name: str,
    include_daily: bool = True,
    include_wtd: bool = True,
    include_mtd: bool = True,
    include_ytd: bool = True,
) -> MultiPeriodMarketData:
    """
    Get market data across multiple time periods

    Args:
        symbol: Ticker symbol (e.g., '^GSPC', 'AAPL')
        name: Display name for the symbol
        include_daily: Include daily change
        include_wtd: Include week-to-date change
        include_mtd: Include month-to-date change
        include_ytd: Include year-to-date change

    Returns:
        MultiPeriodMarketData with data for requested periods
    """
    try:
        # Check market status
        is_open, market_status = is_market_open()

        # Get current price first
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="2d")

        if hist.empty:
            return MultiPeriodMarketData(
                name=name,
                symbol=symbol,
                current_price=0.0,
                market_status=market_status,
                error="No data available",
            )

        current_price = hist["Close"].iloc[-1]

        result = MultiPeriodMarketData(
            name=name,
            symbol=symbol,
            current_price=current_price,
            market_status=market_status,
        )

        # Fetch data for each requested period
        if include_daily:
            result.daily = get_market_data_point(symbol, name, "2d", "Daily")

        if include_wtd:
            result.wtd = get_market_data_point(symbol, name, "5d", "WTD")

        if include_mtd:
            result.mtd = get_market_data_point(symbol, name, "1mo", "MTD")

        if include_ytd:
            result.ytd = get_market_data_point(symbol, name, "1y", "YTD")

        return result

    except Exception as e:
        _, market_status = is_market_open()
        return MultiPeriodMarketData(
            name=name,
            symbol=symbol,
            current_price=0.0,
            market_status=market_status,
            error=str(e),
        )


def format_market_data_point(data: MarketDataPoint, show_price: bool = True) -> str:
    """
    Format a single market data point as markdown

    Args:
        data: MarketDataPoint to format
        show_price: Whether to show the current price

    Returns:
        Formatted markdown string
    """
    if data.error:
        return f"❌ {data.period}: Error - {data.error}\n"

    # Direction and color indicators
    if data.change >= 0:
        direction = "📈"
        color = "🟢"
    else:
        direction = "📉"
        color = "🔴"

    result = f"{color} {direction} **{data.period}**: "

    if show_price:
        result += f"${data.current_price:.2f} "

    result += f"({data.change:+.2f}, {data.change_pct:+.2f}%)\n"

    return result


# DISABLED: format_multi_period_data function - kept for reference but not in use
# def format_multi_period_data(
#     data: MultiPeriodMarketData,
#     compact: bool = False,
# ) -> str:
#     """
#     Format multi-period market data as markdown
#
#     Args:
#         data: MultiPeriodMarketData to format
#         compact: If True, use compact single-line format; if False, use detailed format
#
#     Returns:
#         Formatted markdown string
#     """
#     if data.error:
#         return f"### {data.name} ({data.symbol})\n❌ Error: {data.error}\n\n"
#
#     # Add market status indicator
#     status_emoji = get_market_status_emoji(data.market_status)
#     status_text = data.market_status.replace("_", " ").title()
#
#     result = f"### {data.name} ({data.symbol}) {status_emoji}\n"
#     result += f"**Current Price**: ${data.current_price:.2f} | **Status**: {status_text}\n\n"
#
#     if compact:
#         # Compact format: all periods on one line
#         periods = []
#         for period_data in [data.daily, data.wtd, data.mtd, data.ytd]:
#             if period_data and not period_data.error:
#                 direction = "📈" if period_data.change >= 0 else "📉"
#                 periods.append(
#                     f"{period_data.period}: {direction} {period_data.change_pct:+.2f}%"
#                 )
#
#         if periods:
#             result += " | ".join(periods) + "\n\n"
#     else:
#         # Detailed format: each period on separate line with full info
#         for period_data in [data.daily, data.wtd, data.mtd, data.ytd]:
#             if period_data:
#                 result += format_market_data_point(period_data, show_price=False)
#
#         result += "\n"
#
#     return result


def get_market_overview_with_periods(
    indices: dict[str, str],
    include_daily: bool = True,
    include_wtd: bool = True,
    include_mtd: bool = True,
    include_ytd: bool = True,
    compact: bool = False,
    include_futures_preview: bool = True,
) -> str:
    """
    Get comprehensive market overview with multiple time periods

    Args:
        indices: Dictionary mapping display names to ticker symbols
        include_daily: Include daily changes
        include_wtd: Include week-to-date changes
        include_mtd: Include month-to-date changes
        include_ytd: Include year-to-date changes
        compact: If True, return markdown table format; if False, return JSON format

    Returns:
        Markdown table string (if compact=True) or JSON string (if compact=False)
    """
    # Get market status
    is_open_status, market_status = is_market_open()
    status_emoji = get_market_status_emoji(market_status)
    status_text = market_status.replace("_", " ").title()
    indices_items = tuple(sorted(indices.items()))

    cache_key = (
        "market_overview",
        indices_items,
        include_daily,
        include_wtd,
        include_mtd,
        include_ytd,
        compact,
        include_futures_preview,
        market_status,
    )
    cached_result = _get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    # Format timestamp in ET
    et_tz = ZoneInfo("America/New_York")
    now_et = datetime.now(et_tz)

    # Build market hours info
    market_hours_info = None
    if market_status == "CLOSED":
        market_hours_info = "Monday-Friday, 9:30 AM - 4:00 PM ET"
    elif market_status == "PRE_MARKET":
        market_hours_info = "Pre-Market Trading: 4:00 AM - 9:30 AM ET | Regular hours start soon"
    elif market_status == "AFTER_HOURS":
        market_hours_info = "After-Hours Trading: 4:00 PM - 8:00 PM ET"
    elif market_status == "OPEN":
        market_hours_info = "Market is Open: 9:30 AM - 4:00 PM ET"

    # Collect all market data
    indices_data = []
    for name, symbol in indices.items():
        data = get_multi_period_data(
            symbol=symbol,
            name=name,
            include_daily=include_daily,
            include_wtd=include_wtd,
            include_mtd=include_mtd,
            include_ytd=include_ytd,
        )
        indices_data.append((name, symbol, data))

    # Build futures preview when markets are not fully open
    futures_preview_data: list[tuple[str, str, MultiPeriodMarketData]] = []
    futures_preview_markdown: str | None = None
    futures_preview_json: dict[str, object] | None = None

    should_include_futures = include_futures_preview and market_status in {"PRE_MARKET", "CLOSED"}
    if should_include_futures:
        futures_preview_data = _collect_index_futures_data(
            include_daily=include_daily,
            include_wtd=include_wtd,
            include_mtd=include_mtd,
            include_ytd=include_ytd,
        )

        if compact:
            futures_preview_markdown = _format_index_futures_markdown_table(
                futures_data=futures_preview_data,
                now_et=now_et,
                status_emoji=status_emoji,
                include_daily=include_daily,
                include_wtd=include_wtd,
                include_mtd=include_mtd,
                include_ytd=include_ytd,
            )
        else:
            futures_json_contracts: list[dict[str, object]] = []
            for _, _, data in futures_preview_data:
                contract_dict = asdict(data)
                for period_key in ["daily", "wtd", "mtd", "ytd"]:
                    if contract_dict.get(period_key) and contract_dict[period_key].get("timestamp"):
                        contract_dict[period_key]["timestamp"] = contract_dict[period_key][
                            "timestamp"
                        ].isoformat()
                futures_json_contracts.append(contract_dict)

            futures_preview_json = {
                "as_of": now_et.isoformat(),
                "contracts": futures_json_contracts,
            }

    # Return markdown table format if compact mode
    if compact:
        overview_markdown = _format_as_markdown_table(
            indices_data=indices_data,
            now_et=now_et,
            market_status=market_status,
            status_emoji=status_emoji,
            status_text=status_text,
            market_hours_info=market_hours_info,
            include_daily=include_daily,
            include_wtd=include_wtd,
            include_mtd=include_mtd,
            include_ytd=include_ytd,
        )
        if futures_preview_markdown:
            overview_markdown += "\n\n" + futures_preview_markdown
        ttl = _compute_market_ttl(market_status)
        return _set_cached_result(cache_key, overview_markdown, ttl)

    # Convert to JSON format (default)
    indices_json = []
    for name, symbol, data in indices_data:
        # Convert dataclass to dict and handle nested dataclasses
        data_dict = asdict(data)

        # Convert datetime objects to ISO format strings
        for period_key in ["daily", "wtd", "mtd", "ytd"]:
            if data_dict.get(period_key) and data_dict[period_key].get("timestamp"):
                data_dict[period_key]["timestamp"] = data_dict[period_key]["timestamp"].isoformat()

        indices_json.append(data_dict)

    # Build the final JSON structure
    overview = {
        "timestamp": now_et.isoformat(),
        "timestamp_formatted": now_et.strftime('%Y-%m-%d %H:%M:%S ET'),
        "market_status": {
            "status": market_status,
            "status_text": status_text,
            "status_emoji": status_emoji,
            "is_open": is_open_status,
            "hours_info": market_hours_info,
        },
        "indices": indices_json,
    }

    if futures_preview_json:
        overview["index_futures_preview"] = futures_preview_json

    result_json = json.dumps(overview, indent=2)
    ttl = _compute_market_ttl(market_status)
    return _set_cached_result(cache_key, result_json, ttl)


def _format_as_markdown_table(
    indices_data: list[tuple[str, str, MultiPeriodMarketData]],
    now_et: datetime,
    market_status: str,
    status_emoji: str,
    status_text: str,
    market_hours_info: str | None,
    include_daily: bool,
    include_wtd: bool,
    include_mtd: bool,
    include_ytd: bool,
) -> str:
    """
    Format market data as a compact markdown table

    Args:
        indices_data: List of (name, symbol, MultiPeriodMarketData) tuples
        now_et: Current time in ET timezone
        market_status: Market status code
        status_emoji: Emoji for market status
        status_text: Human-readable market status
        market_hours_info: Market hours information text
        include_daily: Include daily column
        include_wtd: Include WTD column
        include_mtd: Include MTD column
        include_ytd: Include YTD column

    Returns:
        Markdown formatted table string
    """
    result = f"## Market Overview {status_emoji} - {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}\n\n"
    result += f"**Market Status**: {status_text}"
    if market_hours_info:
        result += f" | {market_hours_info}"
    result += "\n\n"

    # Build table header
    header = "| Index | Symbol | Current Price |"
    separator = "|-------|--------|---------------|"

    if include_daily:
        header += " Daily Δ |"
        separator += "---------|"
    if include_wtd:
        header += " WTD Δ |"
        separator += "-------|"
    if include_mtd:
        header += " MTD Δ |"
        separator += "-------|"
    if include_ytd:
        header += " YTD Δ |"
        separator += "-------|"

    result += header + "\n"
    result += separator + "\n"

    # Build table rows
    for name, symbol, data in indices_data:
        if data.error:
            row = f"| {name} | {symbol} | ❌ Error | "
            if include_daily:
                row += "- |"
            if include_wtd:
                row += " - |"
            if include_mtd:
                row += " - |"
            if include_ytd:
                row += " - |"
            result += row + "\n"
            continue

        # Format current price
        row = f"| {name} | {symbol} | ${data.current_price:.2f} |"

        # Add period data
        if include_daily and data.daily:
            if data.daily.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.daily.change >= 0 else "📉"
                row += f" {direction} {data.daily.change_pct:+.2f}% |"
        elif include_daily:
            row += " - |"

        if include_wtd and data.wtd:
            if data.wtd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.wtd.change >= 0 else "📉"
                row += f" {direction} {data.wtd.change_pct:+.2f}% |"
        elif include_wtd:
            row += " - |"

        if include_mtd and data.mtd:
            if data.mtd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.mtd.change >= 0 else "📉"
                row += f" {direction} {data.mtd.change_pct:+.2f}% |"
        elif include_mtd:
            row += " - |"

        if include_ytd and data.ytd:
            if data.ytd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.ytd.change >= 0 else "📉"
                row += f" {direction} {data.ytd.change_pct:+.2f}% |"
        elif include_ytd:
            row += " - |"

        result += row + "\n"

    return result


def _collect_index_futures_data(
    include_daily: bool,
    include_wtd: bool,
    include_mtd: bool,
    include_ytd: bool,
) -> list[tuple[str, str, MultiPeriodMarketData]]:
    """Fetch multi-period data for key equity index futures contracts."""
    futures_data: list[tuple[str, str, MultiPeriodMarketData]] = []
    for name, symbol in INDEX_FUTURES.items():
        data = get_multi_period_data(
            symbol=symbol,
            name=name,
            include_daily=include_daily,
            include_wtd=include_wtd,
            include_mtd=include_mtd,
            include_ytd=include_ytd,
        )
        futures_data.append((name, symbol, data))
    return futures_data


def _format_index_futures_markdown_table(
    futures_data: list[tuple[str, str, MultiPeriodMarketData]],
    now_et: datetime,
    status_emoji: str,
    include_daily: bool,
    include_wtd: bool,
    include_mtd: bool,
    include_ytd: bool,
) -> str:
    """
    Format index futures data as a markdown table suitable for pre-market commentary.
    """
    heading = f"## Index Futures Preview {status_emoji} - {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}\n\n"
    heading += "Overnight moves compared to the prior regular-session close.\n\n"

    header = "| Contract | Symbol | Last Price |"
    separator = "|----------|--------|------------|"

    if include_daily:
        header += " Daily Δ |"
        separator += "---------|"
    if include_wtd:
        header += " WTD Δ |"
        separator += "-------|"
    if include_mtd:
        header += " MTD Δ |"
        separator += "-------|"
    if include_ytd:
        header += " YTD Δ |"
        separator += "-------|"

    rows: list[str] = [header, separator]

    for name, symbol, data in futures_data:
        if data.error:
            row = f"| {name} | {symbol} | ❌ Error |"
            if include_daily:
                row += " ❌ |"
            if include_wtd:
                row += " ❌ |"
            if include_mtd:
                row += " ❌ |"
            if include_ytd:
                row += " ❌ |"
            rows.append(row)
            continue

        row = f"| {name} | {symbol} | ${data.current_price:.2f} |"

        if include_daily and data.daily:
            if data.daily.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.daily.change >= 0 else "📉"
                row += f" {direction} {data.daily.change_pct:+.2f}% |"
        elif include_daily:
            row += " - |"

        if include_wtd and data.wtd:
            if data.wtd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.wtd.change >= 0 else "📉"
                row += f" {direction} {data.wtd.change_pct:+.2f}% |"
        elif include_wtd:
            row += " - |"

        if include_mtd and data.mtd:
            if data.mtd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.mtd.change >= 0 else "📉"
                row += f" {direction} {data.mtd.change_pct:+.2f}% |"
        elif include_mtd:
            row += " - |"

        if include_ytd and data.ytd:
            if data.ytd.error:
                row += " ❌ |"
            else:
                direction = "📈" if data.ytd.change >= 0 else "📉"
                row += f" {direction} {data.ytd.change_pct:+.2f}% |"
        elif include_ytd:
            row += " - |"

        rows.append(row)

    return heading + "\n".join(rows)


def get_index_futures_overview(
    include_daily: bool = True,
    include_wtd: bool = False,
    include_mtd: bool = False,
    include_ytd: bool = False,
    compact: bool = True,
) -> str:
    """
    Public helper for generating an index futures snapshot.

    Args:
        include_daily: Include daily percentage change
        include_wtd: Include week-to-date change
        include_mtd: Include month-to-date change
        include_ytd: Include year-to-date change
        compact: Return markdown table when True, JSON payload when False

    Returns:
        Markdown table string or JSON string with futures data
    """
    _, market_status = is_market_open()
    cache_key = (
        "index_futures_overview",
        include_daily,
        include_wtd,
        include_mtd,
        include_ytd,
        compact,
        market_status,
    )
    cached_result = _get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    status_emoji = get_market_status_emoji(market_status)
    et_tz = ZoneInfo("America/New_York")
    now_et = datetime.now(et_tz)

    futures_data = _collect_index_futures_data(
        include_daily=include_daily,
        include_wtd=include_wtd,
        include_mtd=include_mtd,
        include_ytd=include_ytd,
    )

    if compact:
        result_markdown = _format_index_futures_markdown_table(
            futures_data=futures_data,
            now_et=now_et,
            status_emoji=status_emoji,
            include_daily=include_daily,
            include_wtd=include_wtd,
            include_mtd=include_mtd,
            include_ytd=include_ytd,
        )
        ttl = _compute_market_ttl(market_status)
        return _set_cached_result(cache_key, result_markdown, ttl)

    futures_json = []
    for _, _, data in futures_data:
        contract_dict = asdict(data)
        for period_key in ["daily", "wtd", "mtd", "ytd"]:
            if contract_dict.get(period_key) and contract_dict[period_key].get("timestamp"):
                contract_dict[period_key]["timestamp"] = contract_dict[period_key]["timestamp"].isoformat()
        futures_json.append(contract_dict)

    payload = {
        "timestamp": now_et.isoformat(),
        "market_status": {
            "status": market_status,
            "status_emoji": status_emoji,
        },
        "contracts": futures_json,
    }
    ttl = _compute_market_ttl(market_status)
    return _set_cached_result(cache_key, json.dumps(payload, indent=2), ttl)


def get_stock_analysis_report(symbol: str) -> str:
    """
    Generate detailed stock analysis including fundamentals and recent performance.
    Applies caching to limit repeated calls to yfinance within a short window.
    """
    symbol_upper = symbol.upper()
    _, market_status = is_market_open()
    cache_key = ("stock_analysis", symbol_upper, market_status)
    cached_result = _get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    try:
        ticker = yf.Ticker(symbol_upper)
        info = ticker.info
        hist = ticker.history(period="1mo")

        if hist.empty:
            result = f"No data available for symbol: {symbol}"
            ttl = 180
            return _set_cached_result(cache_key, result, ttl)

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

        # Append "as of" timestamp derived from yfinance metadata or price history.
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

        lines.extend(
            [
            "",
            "### Key Metrics",
            ]
        )

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
            if (
                computed_yield is not None
                and abs(base_yield - computed_yield) > 0.05
            ):
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

    ttl = _compute_equity_ttl(market_status)
    return _set_cached_result(cache_key, result, ttl)


def get_crypto_overview_report(top_n: int = 10) -> str:
    """
    Fetch cryptocurrency market overview using CoinGecko with short-lived caching.
    """
    cache_key = ("crypto_overview", top_n)
    cached_result = _get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    url = "https://api.coingecko.com/api/v3/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": str(top_n),
        "page": "1",
        "sparkline": "False",
    }

    try:
        response = requests.get(url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()
    except Exception as exc:  # noqa: BLE001
        result = f"Error fetching crypto data: {exc!s}"
        return _set_cached_result(cache_key, result, 120)

    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"## Cryptocurrency Overview - {timestamp}\n",
        "### Top Cryptocurrencies by Market Cap\n",
    ]

    for idx, coin in enumerate(data, 1):
        name = coin.get("name", "Unknown")
        symbol = str(coin.get("symbol", "")).upper()
        price = coin.get("current_price", 0.0)
        change_24h = coin.get("price_change_percentage_24h") or 0.0
        market_cap = coin.get("market_cap", 0)
        direction = "📈" if change_24h >= 0 else "📉"

        lines.append(f"**{idx}. {name} ({symbol})**")
        lines.append(f"{direction} ${price:,.4f} ({change_24h:+.2f}%)")
        lines.append(f"Market Cap: ${market_cap:,.0f}\n")

    result = "\n".join(lines)
    return _set_cached_result(cache_key, result, 120)


def get_sector_performance_report() -> str:
    """
    Generate sector performance overview using major sector ETFs with caching.
    """
    _, market_status = is_market_open()
    cache_key = ("sector_performance", market_status)
    cached_result = _get_cached_result(cache_key)
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

    ttl = _compute_equity_ttl(market_status)
    return _set_cached_result(cache_key, result, ttl)
