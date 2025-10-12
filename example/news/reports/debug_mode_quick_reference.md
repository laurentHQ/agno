# Debug Mode Quick Reference

## Quick Set Environment Variable

### Method 1: One-line Command (Temporary)

```bash
# Enable debug mode for single run
DEBUG_MODE=true python src/api/finance_agentos_lite.py

# Or with value "1"
DEBUG_MODE=1 python src/api/finance_agentos_lite.py

# Disable debug mode explicitly
DEBUG_MODE=false python src/api/finance_agentos_lite.py
```

### Method 2: Export (Session-wide)

```bash
# Enable for current shell session
export DEBUG_MODE=true
python src/api/finance_agentos_lite.py

# Disable
export DEBUG_MODE=false
python src/api/finance_agentos_lite.py

# Unset (use config file setting)
unset DEBUG_MODE
python src/api/finance_agentos_lite.py
```

### Method 3: Add to .env File (Persistent)

Edit `.env` file:
```bash
vim .env
```

Uncomment and set:
```bash
# Debug Mode (true/false, 1/0, yes/no, on/off) - Overrides config file setting
DEBUG_MODE=true
```

Then run normally:
```bash
python src/api/finance_agentos_lite.py
```

## Accepted Values

The following values enable debug mode:
- `true`, `True`, `TRUE`
- `1`
- `yes`, `Yes`, `YES`
- `on`, `On`, `ON`

Any other value disables debug mode:
- `false`, `False`, `FALSE`
- `0`
- `no`, `No`, `NO`
- `off`, `Off`, `OFF`
- (empty/unset uses config file setting)

## Priority Order

1. **Environment Variable** (`DEBUG_MODE`) - Highest priority
2. **Config File** (`config/agentos_config.yaml: agent.debug_mode`) - Default
3. **Code Default** (`False`) - Fallback if config missing

## Examples

### Quick Testing with Debug On

```bash
cd example/news
DEBUG_MODE=1 python src/api/finance_agentos_lite.py
```

### Production Run with Debug Off

```bash
cd example/news
DEBUG_MODE=0 python src/api/finance_agentos_lite.py
```

### Use Config File Setting

```bash
cd example/news
# Don't set DEBUG_MODE - will use config/agentos_config.yaml
python src/api/finance_agentos_lite.py
```

## Debug Output Example

With `DEBUG_MODE=true`, you'll see:

```
🔧 Tool: get_market_overview
   Args: {}

📊 Output:
   ## Market Overview - 2025-10-12
   ### S&P 500 (^GSPC)
   🟢 📈 **$5,750.25** (+15.30, +0.27%)

🤔 Reasoning:
   The market shows positive momentum with...
```

## Check Current Setting

Run the config loader test:
```bash
python src/utils/config_loader.py
```

Or check at runtime by looking at agent initialization logs.

## Troubleshooting

**Debug mode not working?**

1. Check environment variable is set:
   ```bash
   echo $DEBUG_MODE
   ```

2. Check .env file is loaded:
   ```bash
   cat .env | grep DEBUG_MODE
   ```

3. Verify config file syntax:
   ```bash
   python src/utils/config_loader.py
   ```

**Debug output too verbose?**

Disable it:
```bash
unset DEBUG_MODE
# or
export DEBUG_MODE=false
```

---

**Last Updated**: 2025-10-12
**Related**: `reports/debug_mode_implementation.md`
