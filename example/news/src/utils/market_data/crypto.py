#!/usr/bin/env python3
"""
Cryptocurrency market overview helper.
"""

from __future__ import annotations

from datetime import datetime

import requests

from .core import get_cached_result, set_cached_result

__all__ = ["get_crypto_overview_report"]


def get_crypto_overview_report(top_n: int = 10) -> str:
    """
    Fetch cryptocurrency market overview using CoinGecko with short-lived caching.
    """
    cache_key = ("crypto_overview", top_n)
    cached_result = get_cached_result(cache_key)
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
        return set_cached_result(cache_key, result, 120)

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
    return set_cached_result(cache_key, result, 120)
