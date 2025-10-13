# Default Model Configuration - OpenAI

This document outlines the configuration changes made to set OpenAI as the default model for the Finance News Agent.

## Configuration Changes

### 1. Agent Function Default (`finance_news_agent.py`)

**File**: `src/agents/finance_news_agent.py`
**Line**: 305

**Before**:
```python
def create_finance_news_agent(model_choice="claude", interactive=False):
```

**After**:
```python
def create_finance_news_agent(model_choice="openai", interactive=False):
```

**Impact**: When creating the finance news agent without specifying a model, it now defaults to OpenAI instead of Claude.

---

### 2. Model Registry Default (`model_selector.py`)

**File**: `src/utils/model_selector.py`
**Lines**: 61-86

**Before**:
```python
MODELS = {
    ModelType.CLAUDE: ModelConfig(
        name="claude",
        display_name="Claude 4.5 Sonnet (Anthropic)",
        model_id="claude-sonnet-4-5",
        env_key="ANTHROPIC_API_KEY",
        description="Default, most stable and reliable",
        is_default=True,  # ← Claude was default
    ),
    ModelType.OPENAI: ModelConfig(
        name="openai",
        display_name="GPT-5 Mini (OpenAI)",
        model_id="gpt-5-mini",
        env_key="OPENAI_API_KEY",
        package_required="openai",
        description="Alternative, requires OpenAI API key",
        # No is_default flag
    ),
    ...
}
```

**After**:
```python
MODELS = {
    ModelType.CLAUDE: ModelConfig(
        name="claude",
        display_name="Claude 4.5 Sonnet (Anthropic)",
        model_id="claude-sonnet-4-5",
        env_key="ANTHROPIC_API_KEY",
        description="Alternative, most stable and reliable",
        # No is_default flag
    ),
    ModelType.OPENAI: ModelConfig(
        name="openai",
        display_name="GPT-5 Mini (OpenAI)",
        model_id="gpt-5-mini",
        env_key="OPENAI_API_KEY",
        package_required="openai",
        description="Default, requires OpenAI API key",
        is_default=True,  # ← OpenAI is now default
    ),
    ...
}
```

**Impact**:
- Interactive model selection shows OpenAI as "Default"
- Pressing Enter during model selection defaults to OpenAI
- Error fallback uses OpenAI instead of Claude

---

### 3. YAML Configuration (`agentos_config.yaml`)

**File**: `config/agentos_config.yaml`
**Line**: 41

**Status**: ✅ Already configured correctly

```yaml
model:
  claude:
    display_name: Claude 4.5 Sonnet (Anthropic)
    max_tokens: 4000
    model_id: claude-sonnet-4-5
    temperature: 0.1
  gemini:
    display_name: Gemini 2.5 Flash (Google)
    max_tokens: 4000
    model_id: gemini-2.5-flash
    temperature: 0.1
  openai:
    display_name: GPT-5 Mini (OpenAI)
    max_tokens: 4000
    model_id: gpt-5-mini
    temperature: 0.1
  primary: openai  # ← OpenAI is already set as primary
```

**Impact**: AgentOS web interface uses OpenAI as the primary model for serving requests.

---

## Verification

### Test Default Model Selection

Run the model selector demo to verify OpenAI is shown as default:

```bash
cd /path/to/agno/example/news
python src/utils/model_selector.py
```

**Expected Output**:
```
🤖 Demo Model Selection:
  1. GPT-5 Mini (OpenAI) - Default (Default, requires OpenAI API key)
  2. Claude 4.5 Sonnet (Anthropic) (Alternative, most stable and reliable)
  3. Gemini 2.5 Flash (Google) (Alternative, requires Google API key)
```

### Test Agent Creation

```python
from src.agents.finance_news_agent import create_finance_news_agent

# Create agent without specifying model - should use OpenAI
agent = create_finance_news_agent()

# Verify model
print(f"Model: {agent.model.__class__.__name__}")  # Should print: OpenAIChat
```

### Test Interactive Mode

```python
# Interactive mode should show OpenAI as default
agent = create_finance_news_agent(interactive=True)

# Press Enter without typing a number - should default to OpenAI
```

---

## Environment Requirements

To use OpenAI as the default model, ensure the following:

### 1. OpenAI API Key

Set the environment variable:
```bash
export OPENAI_API_KEY="your-openai-api-key-here"
```

Or add to `.env` file:
```
OPENAI_API_KEY=your-openai-api-key-here
```

### 2. OpenAI Package

The `openai` package should already be installed as part of the Agno framework dependencies:

```bash
pip install -U agno
```

If not installed separately:
```bash
pip install openai
```

---

## Model Priority Order

After these changes, the model priority is:

1. **OpenAI GPT-5 Mini** (Default)
   - Used when no model is specified
   - Used when pressing Enter during interactive selection
   - Used as fallback for invalid model choices

2. **Claude 4.5 Sonnet** (Alternative)
   - Most stable and reliable
   - Requires Anthropic API key

3. **Gemini 2.5 Flash** (Alternative)
   - Fast and efficient
   - Requires Google API key

---

## Fallback Behavior

If OpenAI is not available (missing API key or package):

1. **Interactive Mode**: Shows available models, user selects manually
2. **Non-Interactive Mode**: Falls back to first available model (Claude if configured)
3. **AgentOS Mode**: Uses configuration from `agentos_config.yaml`

---

## Usage Examples

### Example 1: Default OpenAI
```python
from src.agents.finance_news_agent import create_finance_news_agent

# Creates agent with OpenAI (default)
agent = create_finance_news_agent()
response = agent.run("What's the current market overview?")
```

### Example 2: Explicit Model Choice
```python
# Use Claude explicitly
agent = create_finance_news_agent(model_choice="claude")

# Use Gemini explicitly
agent = create_finance_news_agent(model_choice="gemini")
```

### Example 3: Interactive Selection
```python
# Show interactive menu (OpenAI shown as default)
agent = create_finance_news_agent(interactive=True)
```

---

## Rollback Instructions

To revert to Claude as default:

1. **finance_news_agent.py** (line 305):
   ```python
   def create_finance_news_agent(model_choice="claude", interactive=False):
   ```

2. **model_selector.py** (lines 62-76):
   ```python
   ModelType.CLAUDE: ModelConfig(
       ...
       is_default=True,
   ),
   ModelType.OPENAI: ModelConfig(
       ...
       # Remove is_default=True
   ),
   ```

3. **agentos_config.yaml** (line 41):
   ```yaml
   primary: claude
   ```

---

## Summary

✅ **OpenAI is now the default model** for the Finance News Agent across:
- Direct agent creation
- Interactive model selection
- AgentOS web interface
- Configuration files

All changes maintain backward compatibility - you can still explicitly choose any supported model.
