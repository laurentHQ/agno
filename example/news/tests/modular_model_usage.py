#!/usr/bin/env python3
"""
Example Usage of Modular Model Selection Component
Shows how to integrate the model selector into any agent
"""

import os
from pathlib import Path
import sys

# Add paths for imports from organized structure
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(news_root / "agents"))
sys.path.insert(0, str(news_root / "utils"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def example_basic_usage():
    """Example 1: Basic usage with existing agents"""
    print("📚 Example 1: Basic Usage with Existing Agents")
    print("-" * 50)

    from finance_news_agent import create_finance_news_agent

    # Method 1: Interactive model selection
    print("🔧 Creating finance agent with interactive model selection...")
    try:
        agent = create_finance_news_agent(interactive=True)
        print("✅ Interactive selection completed")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Method 2: Programmatic model selection
    print("\n🔧 Creating finance agent with specific model...")
    try:
        agent_claude = create_finance_news_agent(model_choice="claude")
        agent_openai = create_finance_news_agent(model_choice="openai")
        print("✅ Programmatic selection completed")
    except Exception as e:
        print(f"❌ Failed: {e}")


def example_custom_agent():
    """Example 2: Creating custom agent with model selection"""
    print("\n📚 Example 2: Creating Custom Agent with Model Selection")
    print("-" * 50)

    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.tools.hackernews import HackerNewsTools

    from utils.model_selector import AgentBuilder

    # Define agent components
    tools = [HackerNewsTools(), DuckDuckGoTools(enable_search=True, enable_news=True)]

    instructions = """
    You are a Technology News Analysis Agent.

    Your capabilities:
    1. Search HackerNews for trending tech stories
    2. Find related news articles with DuckDuckGo
    3. Provide insights on technology trends
    4. Analyze startup and developer community discussions

    Focus on:
    - Emerging technologies and innovations
    - Developer tools and frameworks
    - Startup ecosystem news
    - Open source project trends
    """

    # Method 1: Interactive model selection
    print("🔧 Creating custom tech agent with interactive selection...")
    try:
        builder = AgentBuilder(tools=tools, instructions=instructions)
        tech_agent = builder.build_with_model_selection(
            title="Choose AI Model for Tech News Agent", show_descriptions=True
        )
        print("✅ Custom tech agent created with interactive selection")
    except Exception as e:
        print(f"❌ Failed: {e}")

    # Method 2: Specific model selection
    print("\n🔧 Creating custom tech agent with specific model...")
    try:
        from utils.model_selector import ModelType

        builder = AgentBuilder(tools=tools, instructions=instructions)

        if os.getenv("OPENAI_API_KEY"):
            tech_agent_openai = builder.build_with_model_type(ModelType.OPENAI)
            print("✅ Custom tech agent created with OpenAI")

        if os.getenv("ANTHROPIC_API_KEY"):
            tech_agent_claude = builder.build_with_model_type(ModelType.CLAUDE)
            print("✅ Custom tech agent created with Claude")

    except Exception as e:
        print(f"❌ Failed: {e}")


def example_model_info():
    """Example 3: Getting model information and availability"""
    print("\n📚 Example 3: Model Information and Availability")
    print("-" * 50)

    from utils.model_selector import (
        ModelType,
        get_model_selection_info,
    )

    # Get comprehensive model info
    print("📊 Getting model selection information...")
    info = get_model_selection_info()

    print("\n🤖 Available Models:")
    for model_type in ModelType:
        config = info["models"][model_type]
        status = info["availability"][model_type]

        status_icon = "✅" if status["fully_available"] else "❌"
        print(f"  {status_icon} {config.display_name}")
        print(f"     Description: {config.description}")
        print(f"     Package: {'✅' if status['package_available'] else '❌'}")
        print(f"     API Key: {'✅' if status['api_key_available'] else '❌'}")
        print()

    # Show available models
    available = info["available_models"]
    print(f"💡 Fully Available Models: {len(available)}")
    for model_type in available:
        config = info["models"][model_type]
        print(f"   - {config.display_name}")


def example_multi_agent_fleet():
    """Example 4: Creating a fleet of agents with different models"""
    print("\n📚 Example 4: Multi-Agent Fleet with Different Models")
    print("-" * 50)

    from agno.tools.duckduckgo import DuckDuckGoTools
    from agno.tools.hackernews import HackerNewsTools
    from agno.tools.yfinance import YFinanceTools

    from utils.model_selector import AgentBuilder, ModelType

    # Agent configurations
    agent_configs = [
        {
            "name": "Tech News Agent",
            "tools": [HackerNewsTools(), DuckDuckGoTools()],
            "instructions": "You are a technology news specialist focusing on developer trends.",
            "preferred_model": ModelType.CLAUDE,
        },
        {
            "name": "Market Analysis Agent",
            "tools": [YFinanceTools(), DuckDuckGoTools()],
            "instructions": "You are a financial market analyst providing real-time insights.",
            "preferred_model": ModelType.OPENAI,
        },
        {
            "name": "General News Agent",
            "tools": [DuckDuckGoTools(enable_search=True, enable_news=True)],
            "instructions": "You are a general news analyst covering current events.",
            "preferred_model": ModelType.GEMINI,  # Will fallback if not available
        },
    ]

    created_agents = []

    for config in agent_configs:
        print(f"\n🔧 Creating {config['name']}...")
        try:
            builder = AgentBuilder(tools=config["tools"], instructions=config["instructions"])

            # Try preferred model, fallback to available
            try:
                agent = builder.build_with_model_type(config["preferred_model"])
                model_name = config["preferred_model"].value
            except Exception:
                # Fallback to Claude if preferred fails
                agent = builder.build_with_model_type(ModelType.CLAUDE)
                model_name = "claude (fallback)"

            created_agents.append({"name": config["name"], "model": model_name, "agent": agent})
            print(f"✅ {config['name']} created with {model_name}")

        except Exception as e:
            print(f"❌ Failed to create {config['name']}: {e}")

    print(f"\n🎉 Agent Fleet Summary: {len(created_agents)} agents created")
    for agent_info in created_agents:
        print(f"   - {agent_info['name']} ({agent_info['model']})")


def example_advanced_patterns():
    """Example 5: Advanced usage patterns"""
    print("\n📚 Example 5: Advanced Usage Patterns")
    print("-" * 50)

    from utils.model_selector import ModelSelector, create_model_from_choice

    # Custom model selection with specific title
    print("🎯 Custom model selection interface...")
    try:
        selector = ModelSelector(
            title="Choose AI Model for Advanced Agent",
            show_descriptions=False,  # Compact display
        )

        # Get choice mapping without user input (for demo)
        choice_mapping = selector.display_available_models()
        print(f"✅ Choice mapping created: {len(choice_mapping)} options")

    except Exception as e:
        print(f"❌ Failed: {e}")

    # Backward compatibility pattern
    print("\n🔄 Using backward compatibility functions...")
    try:
        model = create_model_from_choice("claude")
        print("✅ Backward compatibility model created")
    except Exception as e:
        print(f"❌ Failed: {e}")


def main():
    """Run all examples"""
    print("🚀 Modular Model Selection Usage Examples")
    print("=" * 60)

    # Check prerequisites
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  No API keys available. Examples will show structure only.")
        print("💡 Set ANTHROPIC_API_KEY or OPENAI_API_KEY to test full functionality")

    # Run examples
    example_basic_usage()
    example_custom_agent()
    example_model_info()
    example_multi_agent_fleet()
    example_advanced_patterns()

    print("\n" + "=" * 60)
    print("🎉 All examples completed!")
    print("\n💡 Key Takeaways:")
    print("  1. Use AgentBuilder for maximum flexibility")
    print("  2. Interactive selection improves user experience")
    print("  3. Programmatic selection enables automation")
    print("  4. Fallback handling ensures robustness")
    print("  5. Model availability checking prevents errors")


if __name__ == "__main__":
    main()
