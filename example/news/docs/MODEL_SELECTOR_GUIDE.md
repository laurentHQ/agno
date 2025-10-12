# Model Selector Guide

A comprehensive modular component for multi-model AI selection across all agents in the Agno News framework.

## 🎯 Overview

The Model Selector utility provides a reusable, consistent interface for selecting and configuring AI models across different agents. It supports Claude (Anthropic), GPT-4 (OpenAI), and Gemini (Google) with automatic availability detection and graceful fallback handling.

## 🚀 Quick Start

### Basic Usage

```python
from utils.model_selector import AgentBuilder
from agno.tools.duckduckgo import DuckDuckGoTools

# Define your agent
tools = [DuckDuckGoTools()]
instructions = "You are a helpful news assistant."

# Create agent with interactive model selection
builder = AgentBuilder(tools=tools, instructions=instructions)
agent = builder.build_with_model_selection()
```

### Programmatic Usage

```python
from utils.model_selector import AgentBuilder, ModelType

builder = AgentBuilder(tools=tools, instructions=instructions)

# Use specific model
agent = builder.build_with_model_type(ModelType.CLAUDE)
agent = builder.build_with_model_type(ModelType.OPENAI)

# Use model by name
agent = builder.build_with_model_name("claude")
agent = builder.build_with_model_name("openai")
```

## 🏗️ Architecture

### Core Components

1. **ModelRegistry**: Centralized model configuration
2. **ModelAvailability**: Package and API key detection
3. **ModelSelector**: Interactive selection interface
4. **ModelFactory**: Model instance creation
5. **AgentBuilder**: High-level agent construction

### Model Configuration

```python
@dataclass
class ModelConfig:
    name: str              # Internal name ("claude", "openai", "gemini")
    display_name: str      # User-friendly name ("Claude (Anthropic)")
    model_id: str         # Specific model ID ("claude-sonnet-4-5")
    env_key: str          # Required environment variable
    package_required: str # Optional package requirement
    description: str      # User description
    is_default: bool      # Whether this is the default model
```

## 🔧 API Reference

### AgentBuilder

Main class for building agents with model selection.

```python
class AgentBuilder:
    def __init__(self, tools: List[Any], instructions: str, markdown: bool = True)

    def build_with_model_selection(self, title: str = "Choose AI Model",
                                   show_descriptions: bool = True) -> Agent

    def build_with_model_type(self, model_type: ModelType) -> Agent

    def build_with_model_name(self, model_name: str) -> Agent
```

### ModelSelector

Interactive model selection interface.

```python
class ModelSelector:
    def __init__(self, title: str = "Choose AI Model", show_descriptions: bool = True)

    def select_model(self) -> ModelType
    def display_available_models(self) -> Dict[str, ModelType]
    def get_user_choice(self, choice_mapping: Dict[str, ModelType]) -> ModelType
```

### Utility Functions

```python
# Get comprehensive model information
info = get_model_selection_info()

# Simple interactive selection
model_type = interactive_model_selection("Choose Model")

# Backward compatibility
model = create_model_from_choice("claude")
```

## 📋 Configuration

### Environment Variables

```bash
# Required for Claude (default)
ANTHROPIC_API_KEY=your_anthropic_key

# Optional for OpenAI
OPENAI_API_KEY=your_openai_key

# Optional for Gemini (requires google-genai package)
GOOGLE_API_KEY=your_google_key
```

### Package Requirements

```bash
# Core (always required)
pip install agno

# For OpenAI support
pip install openai

# For Gemini support
pip install google-genai
```

## 🎨 Usage Patterns

### Pattern 1: Interactive Selection

```python
from utils.model_selector import AgentBuilder
from agno.tools.hackernews import HackerNewsTools

def create_news_agent():
    tools = [HackerNewsTools()]
    instructions = "You are a tech news analyst."

    builder = AgentBuilder(tools=tools, instructions=instructions)
    return builder.build_with_model_selection(
        title="Choose AI Model for News Agent",
        show_descriptions=True
    )

agent = create_news_agent()
```

### Pattern 2: Programmatic Selection

```python
def create_finance_agent(model_choice="claude"):
    tools = [YFinanceTools(), DuckDuckGoTools()]
    instructions = "You are a financial analyst."

    builder = AgentBuilder(tools=tools, instructions=instructions)
    return builder.build_with_model_name(model_choice)

# Create agents with different models
claude_agent = create_finance_agent("claude")
openai_agent = create_finance_agent("openai")
```

### Pattern 3: Multi-Agent Fleet

```python
from utils.model_selector import ModelType

def create_agent_fleet():
    configs = [
        ("Tech Agent", [HackerNewsTools()], ModelType.CLAUDE),
        ("Finance Agent", [YFinanceTools()], ModelType.OPENAI),
        ("News Agent", [DuckDuckGoTools()], ModelType.GEMINI),
    ]

    agents = {}
    for name, tools, preferred_model in configs:
        builder = AgentBuilder(tools=tools, instructions=f"You are a {name}")
        try:
            agents[name] = builder.build_with_model_type(preferred_model)
        except Exception:
            # Fallback to Claude
            agents[name] = builder.build_with_model_type(ModelType.CLAUDE)

    return agents
```

### Pattern 4: Conditional Model Selection

```python
import os
from utils.model_selector import ModelAvailability

def create_optimal_agent():
    available_models = ModelAvailability.get_available_models()

    if ModelType.OPENAI in available_models:
        model_choice = ModelType.OPENAI
    elif ModelType.CLAUDE in available_models:
        model_choice = ModelType.CLAUDE
    else:
        raise RuntimeError("No models available")

    builder = AgentBuilder(tools=tools, instructions=instructions)
    return builder.build_with_model_type(model_choice)
```

## 🔍 Model Information

### Checking Availability

```python
from utils.model_selector import get_model_selection_info

# Get comprehensive model info
info = get_model_selection_info()

print("Available Models:")
for model_type, config in info['models'].items():
    status = info['availability'][model_type]
    print(f"  {config.display_name}: {'✅' if status['fully_available'] else '❌'}")
```

### Runtime Availability Check

```python
from utils.model_selector import ModelAvailability

# Check what's available now
availability = ModelAvailability()
available_models = availability.get_available_models()
status = availability.get_model_status()

print(f"Fully available: {len(available_models)} models")
for model_type in available_models:
    config = ModelRegistry.get_model_config(model_type)
    print(f"  - {config.display_name}")
```

## 🚨 Error Handling

### Graceful Degradation

```python
from utils.model_selector import AgentBuilder, ModelType

def robust_agent_creation():
    builder = AgentBuilder(tools=tools, instructions=instructions)

    # Try preferred model with fallback
    for model_type in [ModelType.OPENAI, ModelType.CLAUDE]:
        try:
            return builder.build_with_model_type(model_type)
        except Exception as e:
            print(f"Failed to create agent with {model_type.value}: {e}")
            continue

    raise RuntimeError("No models available")
```

### API Key Validation

```python
import os
from utils.model_selector import ModelRegistry

def validate_api_keys():
    registry = ModelRegistry()
    missing_keys = []

    for model_type, config in registry.get_all_models().items():
        if not os.getenv(config.env_key):
            missing_keys.append(config.env_key)

    if missing_keys:
        print(f"Missing API keys: {', '.join(missing_keys)}")
        return False
    return True
```

## 🔄 Integration with Existing Agents

### Updating Existing Agents

**Before (hardcoded model):**
```python
def create_agent():
    return Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=tools,
        instructions=instructions,
        markdown=True
    )
```

**After (modular selection):**
```python
def create_agent(model_choice="claude", interactive=False):
    builder = AgentBuilder(tools=tools, instructions=instructions, markdown=True)

    if interactive:
        return builder.build_with_model_selection()
    else:
        return builder.build_with_model_name(model_choice)
```

### Backward Compatibility

```python
from utils.model_selector import create_model_from_choice

# Existing code continues to work
def legacy_create_agent(model_choice="claude"):
    model = create_model_from_choice(model_choice)
    return Agent(model=model, tools=tools, instructions=instructions)
```

## 📊 Best Practices

### 1. Always Handle Errors

```python
try:
    agent = builder.build_with_model_selection()
except RuntimeError as e:
    print(f"Model selection failed: {e}")
    # Fallback logic
```

### 2. Use Environment Detection

```python
if os.getenv("OPENAI_API_KEY"):
    preferred_model = ModelType.OPENAI
else:
    preferred_model = ModelType.CLAUDE
```

### 3. Provide Clear User Feedback

```python
builder = AgentBuilder(tools=tools, instructions=instructions)
agent = builder.build_with_model_selection(
    title="Choose AI Model for Financial Analysis",
    show_descriptions=True
)
```

### 4. Implement Graceful Fallbacks

```python
def create_agent_with_fallback():
    for model_type in [ModelType.OPENAI, ModelType.CLAUDE]:
        try:
            return builder.build_with_model_type(model_type)
        except Exception:
            continue
    raise RuntimeError("No models available")
```

## 🔧 Extending the System

### Adding New Models

1. Update `ModelType` enum:
```python
class ModelType(Enum):
    CLAUDE = "claude"
    OPENAI = "openai"
    GEMINI = "gemini"
    CUSTOM = "custom"  # New model
```

2. Add to `ModelRegistry`:
```python
ModelType.CUSTOM: ModelConfig(
    name="custom",
    display_name="Custom Model",
    model_id="custom-model-id",
    env_key="CUSTOM_API_KEY",
    description="Custom model description"
)
```

3. Update `ModelFactory`:
```python
elif model_type == ModelType.CUSTOM:
    return CustomModel(id=config.model_id)
```

### Custom Selection Interface

```python
class CustomModelSelector(ModelSelector):
    def __init__(self, custom_title: str):
        super().__init__(title=custom_title, show_descriptions=False)

    def custom_selection_logic(self):
        # Your custom logic here
        pass
```

## 📝 Examples

See the complete examples in:
- `examples/test_modular_models.py` - Comprehensive test suite
- `examples/modular_model_usage.py` - Usage patterns and examples
- `agents/finance_news_agent.py` - Integration example

## 🆘 Troubleshooting

### Common Issues

**"No models available"**
- Check API keys are set in environment
- Verify required packages are installed
- Run `python utils/model_selector.py` to check status

**"Package not found" errors**
- Install missing packages: `pip install openai google-genai`
- Check import paths in your environment

**Model selection hangs**
- Handle EOF in non-interactive environments
- Use programmatic selection for automated scripts

**API key errors**
- Verify API keys are valid and have required permissions
- Check environment variable names match exactly

### Debug Information

```python
from utils.model_selector import get_model_selection_info

# Get debug info
info = get_model_selection_info()
print("Debug Info:")
print(f"  Package availability: {info['package_availability']}")
print(f"  API key availability: {info['api_key_availability']}")
print(f"  Available models: {[m.value for m in info['available_models']]}")
```

---

## 📄 License

This component is part of the Agno News Agent framework and follows the same license terms.