#!/usr/bin/env python3
"""
Core market data utilities: caching, market hours, data types, and formatting helpers.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import Any, Literal, NamedTuple
from zoneinfo import ZoneInfo

import yfinance as yf

__all__ = [
    "MarketDataPoint",
    "MultiPeriodMarketData",
    "format_market_data_point",
    "get_market_data_point",
    "get_multi_period_data",
    "get_market_status_emoji",
    "get_cached_result",
    "set_cached_result",
    "compute_market_ttl",
    "compute_equity_ttl",
    "is_market_open",
    "_format_percent",
    "_format_price",
    "_normalize_percent_value",
    "_build_premarket_section",
    "_build_postmarket_section",
]


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


def compute_market_ttl(status: str) -> int:
    """Determine cache TTL based on market status for timely refresh."""
    if status == "OPEN":
        return 60
    if status in {"PRE_MARKET", "AFTER_HOURS"}:
        return 180
    return 600


def compute_equity_ttl(status: str) -> int:
    """TTL tuning for single-stock or sector snapshots."""
    if status == "OPEN":
        return 120
    if status in {"PRE_MARKET", "AFTER_HOURS"}:
        return 300
    return 600


def set_cached_result(cache_key: tuple[Any, ...], value: Any, ttl_seconds: int) -> Any:
    """Persist cached results using tuple-based cache key."""
    key_str = repr(cache_key)
    return _set_cache(key_str, value, ttl_seconds)


def get_cached_result(cache_key: tuple[Any, ...]) -> Any | None:
    """Retrieve cached value given tuple-based cache key."""
    key_str = repr(cache_key)
    return _get_cache(key_str)


def is_market_open(market: str = "US") -> tuple[bool, str]:
    """
    Check if the market is currently open.

    Returns tuple (is_open, status)
    """
    try:
        et_tz = ZoneInfo("America/New_York")
        now_et = datetime.now(et_tz)

        if now_et.weekday() >= 5:  # 5=Saturday, 6=Sunday
            return False, "CLOSED"

        current_time = now_et.time()
        pre_market_open = datetime.strptime("04:00", "%H:%M").time()
        market_open = datetime.strptime("09:30", "%H:%M").time()
        market_close = datetime.strptime("16:00", "%H:%M").time()
        after_hours_close = datetime.strptime("20:00", "%H:%M").time()

        if market_open <= current_time < market_close:
            return True, "OPEN"
        if pre_market_open <= current_time < market_open:
            return False, "PRE_MARKET"
        if market_close <= current_time < after_hours_close:
            return False, "AFTER_HOURS"
        return False, "CLOSED"

    except Exception:
        return False, "CLOSED"


def get_market_status_emoji(status: str) -> str:
    """Get emoji indicator for market status."""
    status_map = {
        "OPEN": "🔔",
        "CLOSED": "🔕",
        "PRE_MARKET": "🌅",
        "AFTER_HOURS": "🌙",
    }
    return status_map.get(status, "❓")


@dataclass
class MarketDataPoint:
    """Represents market data for a specific time period."""

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
    """Market data across multiple time periods."""

    name: str
    symbol: str
    current_price: float
    daily: MarketDataPoint | None = None
    wtd: MarketDataPoint | None = None
    mtd: MarketDataPoint | None = None
    ytd: MarketDataPoint | None = None
    market_status: str = "CLOSED"
    error: str | None = None


def _format_percent(value: float) -> str:
    """Format numeric value as percentage, correcting for plain percent inputs."""
    if value is None:
        return "N/A"
    percent_value = value / 100 if abs(value) >= 1 else value
    return f"{percent_value:.2%}"


def _format_price(value: float, symbol: str) -> str:
    """Format price values with appropriate precision based on instrument type."""
    if symbol.endswith("=X"):
        return f"{value:,.4f}"
    return f"${value:,.2f}"


def _normalize_percent_value(value: float | None) -> float | None:
    """Convert percentage-like values into true percentage representation."""
    if value is None:
        return None
    if abs(value) >= 1:
        return float(value)
    return float(value) * 100


def _build_extended_hours_section(
    info: dict[str, object],
    ticker: yf.Ticker,
    previous_close: float | None,
    session: Literal["pre", "post"],
) -> list[str]:
    """Build pre-market or post-market section depending on session flag."""
    price: float | None = None
    timestamp: float | None = None
    change_value: float | None = None
    change_percent: float | None = None

    prefix = "preMarket" if session == "pre" else "postMarket"

    info_price = info.get(f"{prefix}Price")
    if isinstance(info_price, (int, float)):
        price = float(info_price)

    info_time = info.get(f"{prefix}Time")
    if isinstance(info_time, (int, float)):
        timestamp = float(info_time)

    info_change = info.get(f"{prefix}Change")
    if isinstance(info_change, (int, float)):
        change_value = float(info_change)

    info_change_pct = info.get(f"{prefix}ChangePercent")
    if isinstance(info_change_pct, (int, float)):
        change_percent = _normalize_percent_value(float(info_change_pct))

    fast_info = getattr(ticker, "fast_info", None) if hasattr(ticker, "fast_info") else None
    if price is None and fast_info is not None:
        fi_price = getattr(fast_info, f"{session}_market_price", None)
        if isinstance(fi_price, (int, float)):
            price = float(fi_price)

    if timestamp is None and fast_info is not None:
        fi_time = getattr(fast_info, f"{session}_market_time", None)
        if isinstance(fi_time, (int, float)):
            timestamp = float(fi_time)

    if change_value is None and fast_info is not None:
        fi_change = getattr(fast_info, f"{session}_market_change", None)
        if isinstance(fi_change, (int, float)):
            change_value = float(fi_change)

    if change_percent is None and fast_info is not None:
        fi_change_pct = getattr(fast_info, f"{session}_market_change_percent", None)
        if isinstance(fi_change_pct, (int, float)):
            change_percent = _normalize_percent_value(float(fi_change_pct))

    if price is None:
        return []

    base_previous_close: float | None = None
    if isinstance(previous_close, (int, float)) and previous_close:
        base_previous_close = float(previous_close)
    else:
        prev_close_candidate = info.get("regularMarketPreviousClose") or info.get("previousClose")
        if isinstance(prev_close_candidate, (int, float)) and prev_close_candidate:
            base_previous_close = float(prev_close_candidate)

    if base_previous_close:
        computed_change = price - base_previous_close
        computed_change_pct = (computed_change / base_previous_close) * 100 if base_previous_close else None
        change_value = computed_change
        if computed_change_pct is not None:
            change_percent = computed_change_pct

    if change_value is None and change_percent is None:
        return []

    change_value_text = f"{change_value:+.2f}" if change_value is not None else "N/A"
    change_percent_text = f"{change_percent:+.2f}%" if change_percent is not None else "N/A"
    direction_value = change_value if change_value is not None else change_percent or 0.0
    icon = "🌅📈" if session == "pre" else "🌙📈"
    if direction_value < 0:
        icon = "🌅📉" if session == "pre" else "🌙📉"

    heading = "Pre-Market" if session == "pre" else "After-Hours"
    section_lines = [
        f"### {heading}",
        f"{icon} **${price:.2f}** ({change_value_text}, {change_percent_text})",
    ]

    if timestamp:
        try:
            dt = datetime.fromtimestamp(timestamp, tz=timezone.utc).astimezone(
                ZoneInfo("America/New_York")
            )
            section_lines.append(f"**{heading} As of**: {dt.strftime('%Y-%m-%d %H:%M %Z')}")
        except Exception:
            pass

    return section_lines


def _build_premarket_section(
    info: dict[str, object],
    ticker: yf.Ticker,
    previous_close: float | None,
) -> list[str]:
    """Construct pre-market section lines when pre-market data is available."""
    return _build_extended_hours_section(info=info, ticker=ticker, previous_close=previous_close, session="pre")


def _build_postmarket_section(
    info: dict[str, object],
    ticker: yf.Ticker,
    previous_close: float | None,
) -> list[str]:
    """Construct after-hours section lines when post-market data is available."""
    return _build_extended_hours_section(info=info, ticker=ticker, previous_close=previous_close, session="post")


def _build_market_data_point_from_previous_close(
    ticker: yf.Ticker, name: str, symbol: str, period_label: str
) -> MarketDataPoint | None:
    """Build a MarketDataPoint using regularMarketPreviousClose when history is insufficient."""
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

    if symbol.endswith("=X"):
        last_price = round(last_price, 4)
        previous_close = round(previous_close, 4)
        change = round(change, 4)
        change_pct = round(change_pct, 4)

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


def get_market_data_point(
    symbol: str,
    name: str,
    period: Literal["1d", "2d", "5d", "1mo", "1y"],
    period_label: str,
) -> MarketDataPoint | None:
    """Get market data for a specific symbol and time period."""
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
        is_currency_pair = symbol.endswith("=X")

        previous_close = None
        if period_label == "Daily":
            previous_close = hist["Close"].iloc[-2] if len(hist) >= 2 else hist["Close"].iloc[0]
            start_price = previous_close
        else:
            start_price = hist["Close"].iloc[0]

        change = current_price - start_price
        change_pct = (change / start_price) * 100 if start_price != 0 else 0.0

        if is_currency_pair:
            current_price = round(current_price, 4)
            change = round(change, 4)
            if previous_close is not None:
                previous_close = round(previous_close, 4)
            change_pct = round(change_pct, 4)

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

    except Exception as exc:
        return MarketDataPoint(
            name=name,
            symbol=symbol,
            current_price=0.0,
            change=0.0,
            change_pct=0.0,
            period=period_label,
            timestamp=datetime.now(),
            error=str(exc),
        )


def get_multi_period_data(
    symbol: str,
    name: str,
    include_daily: bool = True,
    include_wtd: bool = True,
    include_mtd: bool = True,
    include_ytd: bool = True,
) -> MultiPeriodMarketData:
    """Get market data across multiple time periods."""
    try:
        _, market_status = is_market_open()
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

        if include_daily:
            result.daily = get_market_data_point(symbol, name, "2d", "Daily")
        if include_wtd:
            result.wtd = get_market_data_point(symbol, name, "5d", "WTD")
        if include_mtd:
            result.mtd = get_market_data_point(symbol, name, "1mo", "MTD")
        if include_ytd:
            result.ytd = get_market_data_point(symbol, name, "1y", "YTD")

        return result

    except Exception as exc:
        _, market_status = is_market_open()
        return MultiPeriodMarketData(
            name=name,
            symbol=symbol,
            current_price=0.0,
            market_status=market_status,
            error=str(exc),
        )


def format_market_data_point(data: MarketDataPoint, show_price: bool = True) -> str:
    """Format a single market data point as markdown."""
    if data.error:
        return f"❌ {data.period}: Error - {data.error}\n"

    direction = "📈" if data.change >= 0 else "📉"
    color = "🟢" if data.change >= 0 else "🔴"
    result = f"{color} {direction} **{data.period}**: "

    if show_price:
        result += f"{_format_price(data.current_price, data.symbol)} "

    result += f"({data.change:+.2f}, {data.change_pct:+.2f}%)\n"
    return result
