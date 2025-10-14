#!/usr/bin/env python3
"""
Market overview builders, including index futures preview.
"""

from __future__ import annotations

import json
from dataclasses import asdict
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Any

from .core import (
    MultiPeriodMarketData,
    compute_market_ttl,
    format_market_data_point,
    get_cached_result,
    get_market_status_emoji,
    get_multi_period_data,
    is_market_open,
    set_cached_result,
    _format_price,
)

__all__ = [
    "get_market_overview_with_periods",
    "get_index_futures_overview",
]

# Equity index futures contracts used for pre-market insight
INDEX_FUTURES: dict[str, str] = {
    "S&P 500 Futures": "ES=F",
    "Dow Futures": "YM=F",
    "Nasdaq 100 Futures": "NQ=F",
    "Russell 2000 Futures": "RTY=F",
}


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
    Get comprehensive market overview with multiple time periods.
    """
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
    cached_result = get_cached_result(cache_key)
    if cached_result is not None:
        return cached_result

    et_tz = ZoneInfo("America/New_York")
    now_et = datetime.now(et_tz)

    market_hours_info = None
    if market_status == "CLOSED":
        market_hours_info = "Monday-Friday, 9:30 AM - 4:00 PM ET"
    elif market_status == "PRE_MARKET":
        market_hours_info = "Pre-Market Trading: 4:00 AM - 9:30 AM ET | Regular hours start soon"
    elif market_status == "AFTER_HOURS":
        market_hours_info = "After-Hours Trading: 4:00 PM - 8:00 PM ET"
    elif market_status == "OPEN":
        market_hours_info = "Market is Open: 9:30 AM - 4:00 PM ET"

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

    futures_preview_markdown: str | None = None
    futures_preview_json: dict[str, Any] | None = None

    should_include_futures = include_futures_preview and market_status in {"PRE_MARKET", "CLOSED"}
    futures_preview_data: list[tuple[str, str, MultiPeriodMarketData]] = []

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
            futures_json_contracts: list[dict[str, Any]] = []
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
        ttl = compute_market_ttl(market_status)
        return set_cached_result(cache_key, overview_markdown, ttl)

    indices_json = []
    for name, symbol, data in indices_data:
        data_dict = asdict(data)
        for period_key in ["daily", "wtd", "mtd", "ytd"]:
            if data_dict.get(period_key) and data_dict[period_key].get("timestamp"):
                data_dict[period_key]["timestamp"] = data_dict[period_key]["timestamp"].isoformat()
        indices_json.append(data_dict)

    overview = {
        "timestamp": now_et.isoformat(),
        "timestamp_formatted": now_et.strftime("%Y-%m-%d %H:%M:%S ET"),
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
    ttl = compute_market_ttl(market_status)
    return set_cached_result(cache_key, result_json, ttl)


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
    """Format market data as a compact markdown table."""
    result = f"## Market Overview {status_emoji} - {now_et.strftime('%Y-%m-%d %H:%M:%S ET')}\n\n"
    result += f"**Market Status**: {status_text}"
    if market_hours_info:
        result += f" | {market_hours_info}"
    result += "\n\n"

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

        row = f"| {name} | {symbol} | {_format_price(data.current_price, symbol)} |"

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
    """Format index futures data as a markdown table suitable for pre-market commentary."""
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

        row = f"| {name} | {symbol} | {_format_price(data.current_price, symbol)} |"

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
    """Public helper for generating an index futures snapshot."""
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
    cached_result = get_cached_result(cache_key)
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
        ttl = compute_market_ttl(market_status)
        return set_cached_result(cache_key, result_markdown, ttl)

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
    ttl = compute_market_ttl(market_status)
    return set_cached_result(cache_key, json.dumps(payload, indent=2), ttl)
