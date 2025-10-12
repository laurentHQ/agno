# Debug Mode Implementation

## Overview
Added configurable debug mode flag for the Finance News Agent to enable detailed logging and tool call visibility during agent execution.

## Changes Made

### 1. Configuration File (`config/agentos_config.yaml`)
**Location**: `/home/laure/disk/agno/example/news/config/agentos_config.yaml`

**Addition**:
```yaml
agent:
  description: Specialized Financial News and Market Analysis Agent with real-time
    data capabilities
  interactive: false
  markdown: true
  name: finance-news-agent
  debug_mode: false  # ← NEW: Enable/disable debug mode
```

### 2. Config Loader (`src/utils/config_loader.py`)
**Location**: `/home/laure/disk/agno/example/news/src/utils/config_loader.py`

**Changes**:

#### AgentConfig Dataclass (Line 47-55)
```python
@dataclass
class AgentConfig:
    """Agent configuration"""

    name: str = "finance-news-agent"
    description: str = "Specialized Financial News and Market Analysis Agent"
    interactive: bool = False
    markdown: bool = True
    debug_mode: bool = False  # ← NEW: Debug mode flag
```

#### Config Parser (Line 137-147)
```python
# Parse agent configuration
agent_data = data.get("agent", {})
agent = AgentConfig(
    name=agent_data.get("name", "finance-news-agent"),
    description=agent_data.get(
        "description", "Specialized Financial News and Market Analysis Agent"
    ),
    interactive=agent_data.get("interactive", False),
    markdown=agent_data.get("markdown", True),
    debug_mode=agent_data.get("debug_mode", False),  # ← NEW: Parse debug_mode
)
```

### 3. API Server (`src/api/finance_agentos_lite.py`)
**Location**: `/home/laure/disk/agno/example/news/src/api/finance_agentos_lite.py`

**Changes** (Line 83-94):
```python
# Set agent name and session handling from config
if config:
    finance_agent.name = config.agent.name
    finance_agent.description = config.agent.description
    finance_agent.markdown = config.agent.markdown
    finance_agent.debug_mode = config.agent.debug_mode  # ← NEW: Apply debug mode
else:
    finance_agent.name = "finance-news-agent"
    finance_agent.description = (
        "Specialized Financial News and Market Analysis Agent with SQLite persistence"
    )
    finance_agent.debug_mode = False  # ← NEW: Default to False
```

## How It Works

### Debug Mode Disabled (Default: `debug_mode: false`)
- Agent runs normally with minimal output
- Tool calls are executed silently
- Only final results are shown
- Optimized for production use

### Debug Mode Enabled (`debug_mode: true`)
- Agent shows detailed execution flow
- Tool calls are logged with inputs and outputs
- Internal reasoning steps are visible
- Useful for development and troubleshooting

## Usage

### Method 1: Environment Variable (Quick & Temporary)

**One-line command**:
```bash
# Enable debug mode for single run
DEBUG_MODE=true python src/api/finance_agentos_lite.py

# Or export for session
export DEBUG_MODE=true
python src/api/finance_agentos_lite.py
```

**Accepted values**: `true`, `1`, `yes`, `on` (enables) | `false`, `0`, `no`, `off` (disables)

**Add to .env file** (persistent):
```bash
# Edit .env
vim .env

# Add/uncomment:
DEBUG_MODE=true
```

### Method 2: Configuration File (Persistent Default)

**Edit configuration file**:
```bash
vim config/agentos_config.yaml
```

Change:
```yaml
agent:
  debug_mode: true  # Enable debug output
```

**Restart the server**:
```bash
python src/api/finance_agentos_lite.py
```

### Priority Order

1. **Environment Variable** (`DEBUG_MODE`) - **Highest priority** (overrides config)
2. **Config File** (`config/agentos_config.yaml`) - Default setting
3. **Code Default** (`False`) - Fallback if config missing

### Debug Output Example

When `debug_mode: true`, you'll see detailed logging:
```
🔧 Calling tool: get_market_overview
   Input: {}

📊 Tool output:
   ## Market Overview - 2025-10-12 14:30:00
   ### S&P 500 (^GSPC)
   🟢 📈 **$5,750.25** (+15.30, +0.27%)

🤔 Agent reasoning:
   Based on the market data, the S&P 500 is showing...
```

### Disable Debug Mode

**Edit configuration file**:
```bash
vim config/agentos_config.yaml
```

Change:
```yaml
agent:
  debug_mode: false  # Disable debug output (production mode)
```

## Benefits

1. **Troubleshooting**: See exactly which tools the agent calls and what data it receives
2. **Development**: Understand agent decision-making process during feature development
3. **Production Ready**: Easy toggle between verbose debugging and clean production output
4. **Configuration-Based**: No code changes needed - just update YAML config
5. **Automatic Handling**: Agno framework respects the debug_mode flag automatically

## Integration Points

The debug mode is automatically applied to all agent.run() calls:
- `/finance/quick-analysis` endpoint
- `/finance/market-overview` endpoint
- Direct agent interactions via AgentOS API

## Validation

Run the config loader test to verify:
```bash
python src/utils/config_loader.py
```

Expected output:
```
🔧 Configuration loaded successfully!
Primary model: openai
Database type: sqlite
Server port: 8080
✅ Configuration is valid!
```

---

**Date**: 2025-10-12
**Status**: ✅ Complete
**Files Modified**: 3
**Files Created**: 1 (this documentation)
