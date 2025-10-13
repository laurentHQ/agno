# Market Overview Output Formats

The `get_market_overview()` tool now supports dual output formats for maximum flexibility.

## Output Format Options

### 1. JSON Format (Default)
**Usage**: `compact=False` (default parameter)

**Best for**:
- Programmatic data access
- Data processing and calculations
- Extracting specific metrics
- API integrations

**Structure**:
```json
{
  "timestamp": "2025-10-13T14:30:00-04:00",
  "timestamp_formatted": "2025-10-13 14:30:00 ET",
  "market_status": {
    "status": "OPEN",
    "status_text": "Open",
    "status_emoji": "🔔",
    "is_open": true,
    "hours_info": "Market is Open: 9:30 AM - 4:00 PM ET"
  },
  "indices": [
    {
      "name": "S&P 500",
      "symbol": "^GSPC",
      "current_price": 4500.00,
      "daily": {
        "name": "S&P 500",
        "symbol": "^GSPC",
        "current_price": 4500.00,
        "change": 25.50,
        "change_pct": 0.57,
        "period": "Daily",
        "timestamp": "2025-10-13T14:30:00-04:00",
        "error": null
      },
      "wtd": {...},
      "mtd": {...},
      "ytd": {...},
      "market_status": "OPEN",
      "error": null
    }
  ]
}
```

### 2. Markdown Table Format (Compact Mode)
**Usage**: `compact=True`

**Best for**:
- Human-readable reports
- Visual summaries
- Quick market snapshots
- User-facing displays

**Example Output**:
```markdown
## Market Overview 🔔 - 2025-10-13 14:30:00 ET

**Market Status**: Open | Market is Open: 9:30 AM - 4:00 PM ET

| Index | Symbol | Current Price | Daily Δ | WTD Δ | MTD Δ | YTD Δ |
|-------|--------|---------------|---------|-------|-------|-------|
| S&P 500 | ^GSPC | $4500.00 | 📈 +0.57% | 📈 +1.23% | 📈 +2.45% | 📈 +15.67% |
| Dow Jones | ^DJI | $35000.00 | 📉 -0.23% | 📈 +0.89% | 📈 +1.78% | 📈 +12.34% |
| NASDAQ | ^IXIC | $14000.00 | 📈 +0.89% | 📈 +1.56% | 📈 +3.21% | 📈 +18.90% |
```

## Function Parameters

```python
def get_market_overview(
    include_daily: bool = True,    # Include daily changes
    include_wtd: bool = True,      # Include week-to-date changes
    include_mtd: bool = True,      # Include month-to-date changes
    include_ytd: bool = True,      # Include year-to-date changes
    compact: bool = False,         # False=JSON, True=Markdown table
) -> str:
```

## Usage Examples

### Example 1: JSON Format (All Periods)
```python
from finance_news_agent import AdvancedFinanceTools

tools = AdvancedFinanceTools()
result = tools.get_market_overview(compact=False)

# Parse JSON for data processing
import json
data = json.loads(result)
print(f"Market Status: {data['market_status']['status_text']}")
print(f"S&P 500: ${data['indices'][0]['current_price']:.2f}")
```

### Example 2: Markdown Table (All Periods)
```python
tools = AdvancedFinanceTools()
result = tools.get_market_overview(compact=True)

# Display as markdown - ready for reports
print(result)
```

### Example 3: Markdown Table (Daily Only)
```python
result = tools.get_market_overview(
    include_daily=True,
    include_wtd=False,
    include_mtd=False,
    include_ytd=False,
    compact=True
)
```

### Example 4: Markdown Table (Selected Periods)
```python
result = tools.get_market_overview(
    include_daily=True,
    include_wtd=False,
    include_mtd=False,
    include_ytd=True,  # Show only Daily and YTD
    compact=True
)
```

## Visual Indicators

Both formats include rich visual indicators:

- **Market Status**: 🔔 OPEN, 🔕 CLOSED, 🌅 PRE_MARKET, 🌙 AFTER_HOURS
- **Trend Direction**: 📈 (positive), 📉 (negative)
- **Error Handling**: ❌ (when data unavailable)

## Covered Markets

The tool tracks:

### US Indices
- S&P 500 (^GSPC)
- Dow Jones (^DJI)
- NASDAQ (^IXIC)
- Russell 2000 (^RUT)
- VIX Volatility Index (^VIX)

### Global Indices
- Hang Seng (^HSI)
- EURO STOXX 50 (^STOXX50E)

### Currencies
- EUR/USD (EURUSD=X)
- US Dollar Index (DX-Y.NYB)

### Commodities
- Gold (GC=F)
- Crude Oil WTI (CL=F)

## Implementation Details

### File Structure
- **Core Logic**: `src/utils/market_data_utils.py`
- **Agent Integration**: `src/agents/finance_news_agent.py`
- **Tests**: `tests/test_market_overview.py`

### Key Functions
1. `get_market_overview_with_periods()` - Main function with dual format support
2. `_format_as_markdown_table()` - Markdown table formatter
3. `get_multi_period_data()` - Fetches multi-period market data
4. `is_market_open()` - Market status detection

## Testing

Run the test suite to see both formats in action:

```bash
cd /path/to/agno/example/news
python tests/test_market_overview.py
```

The test demonstrates:
1. JSON format with all periods
2. Markdown table with all periods
3. Markdown table with daily only
4. Markdown table with selected periods (Daily + YTD)

## Migration Notes

Previous versions used a disabled `format_multi_period_data()` function. The new implementation:

- ✅ Provides structured JSON for programmatic access
- ✅ Provides clean markdown tables for visual display
- ✅ Maintains backward compatibility with existing parameters
- ✅ Enhanced with market status and emoji indicators
- ✅ Supports flexible period selection

## Future Enhancements

Potential additions:
- CSV export format
- Custom column ordering
- Color coding for terminal output
- Additional market sectors
- Historical comparison views
