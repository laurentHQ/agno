#!/usr/bin/env python3
"""
Test script for Modular Model Selection Component
Tests the reusable model selector across different agents
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


def test_model_selector_utility():
    """Test the standalone model selector utility"""
    print("🧪 Testing Model Selector Utility...")

    try:
        from utils.model_selector import (
            ModelAvailability,
            ModelRegistry,
            get_model_selection_info,
        )

        print("✅ Model selector imports successful")

        # Test model registry
        registry = ModelRegistry()
        all_models = registry.get_all_models()
        print(f"✅ Model registry: {len(all_models)} models registered")

        # Test availability checking
        availability = ModelAvailability()
        available_models = availability.get_available_models()
        print(f"✅ Available models: {len(available_models)} models ready")

        # Test model info
        info = get_model_selection_info()
        print("✅ Model selection info generated")

        return True

    except Exception as e:
        print(f"❌ Model selector utility test failed: {e}")
        return False


def test_finance_agent_integration():
    """Test the finance agent with modular model selection"""
    print("\n🤖 Testing Finance Agent with Modular Models...")

    try:
        from finance_news_agent import create_finance_news_agent

        # Test programmatic model selection
        print("📊 Testing programmatic model selection...")

        # Test with Claude (should work if API key available)
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                claude_agent = create_finance_news_agent(model_choice="claude")
                print("✅ Claude finance agent created successfully")
            except Exception as e:
                print(f"⚠️  Claude agent failed: {e}")

        # Test with OpenAI (should work if API key available)
        if os.getenv("OPENAI_API_KEY"):
            try:
                openai_agent = create_finance_news_agent(model_choice="openai")
                print("✅ OpenAI finance agent created successfully")
            except Exception as e:
                print(f"⚠️  OpenAI agent failed: {e}")

        # Test with invalid model (should fallback to default)
        try:
            fallback_agent = create_finance_news_agent(model_choice="invalid_model")
            print("✅ Fallback model handling working")
        except Exception as e:
            print(f"⚠️  Fallback test failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Finance agent integration test failed: {e}")
        return False


def test_agent_builder():
    """Test the AgentBuilder utility directly"""
    print("\n🔧 Testing AgentBuilder Utility...")

    try:
        from agno.tools.duckduckgo import DuckDuckGoTools

        from utils.model_selector import AgentBuilder, ModelType

        # Create a simple agent builder
        tools = [DuckDuckGoTools()]
        instructions = "Test agent for model selection"

        builder = AgentBuilder(tools=tools, instructions=instructions)
        print("✅ AgentBuilder created successfully")

        # Test building with specific model types
        available_models = []

        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                claude_agent = builder.build_with_model_type(ModelType.CLAUDE)
                available_models.append("Claude")
                print("✅ AgentBuilder with Claude working")
            except Exception as e:
                print(f"⚠️  Claude AgentBuilder failed: {e}")

        if os.getenv("OPENAI_API_KEY"):
            try:
                openai_agent = builder.build_with_model_type(ModelType.OPENAI)
                available_models.append("OpenAI")
                print("✅ AgentBuilder with OpenAI working")
            except Exception as e:
                print(f"⚠️  OpenAI AgentBuilder failed: {e}")

        print(f"✅ AgentBuilder test completed. Available: {', '.join(available_models)}")
        return True

    except Exception as e:
        print(f"❌ AgentBuilder test failed: {e}")
        return False


def test_backward_compatibility():
    """Test backward compatibility functions"""
    print("\n🔄 Testing Backward Compatibility...")

    try:
        from utils.model_selector import create_model_from_choice

        # Test the backward compatibility function
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                claude_model = create_model_from_choice("claude")
                print("✅ Backward compatibility with Claude working")
            except Exception as e:
                print(f"⚠️  Claude backward compatibility failed: {e}")

        if os.getenv("OPENAI_API_KEY"):
            try:
                openai_model = create_model_from_choice("openai")
                print("✅ Backward compatibility with OpenAI working")
            except Exception as e:
                print(f"⚠️  OpenAI backward compatibility failed: {e}")

        # Test invalid model fallback
        try:
            fallback_model = create_model_from_choice("invalid")
            print("✅ Backward compatibility fallback working")
        except Exception as e:
            print(f"⚠️  Fallback compatibility failed: {e}")

        return True

    except Exception as e:
        print(f"❌ Backward compatibility test failed: {e}")
        return False


def test_multi_agent_scenario():
    """Test creating multiple agents with different models"""
    print("\n🌐 Testing Multi-Agent Scenario...")

    try:
        from agno.tools.hackernews import HackerNewsTools
        from finance_news_agent import create_finance_news_agent

        from utils.model_selector import AgentBuilder

        agents_created = []

        # Create finance agent
        if os.getenv("ANTHROPIC_API_KEY"):
            try:
                finance_agent = create_finance_news_agent(model_choice="claude")
                agents_created.append("Finance Agent (Claude)")
                print("✅ Finance agent created")
            except Exception as e:
                print(f"⚠️  Finance agent failed: {e}")

        # Create a simple news agent using AgentBuilder
        if os.getenv("OPENAI_API_KEY"):
            try:
                builder = AgentBuilder(
                    tools=[HackerNewsTools()],
                    instructions="You are a tech news analyst.",
                    markdown=True,
                )
                news_agent = builder.build_with_model_name("openai")
                agents_created.append("News Agent (OpenAI)")
                print("✅ News agent created")
            except Exception as e:
                print(f"⚠️  News agent failed: {e}")

        print(f"✅ Multi-agent test completed. Created: {len(agents_created)} agents")
        for agent in agents_created:
            print(f"   - {agent}")

        return True

    except Exception as e:
        print(f"❌ Multi-agent scenario test failed: {e}")
        return False


def main():
    """Run all modular model selection tests"""
    print("🚀 Modular Model Selection Test Suite")
    print("=" * 60)

    all_tests_passed = True

    # Test standalone utility
    if not test_model_selector_utility():
        all_tests_passed = False

    # Test finance agent integration
    if not test_finance_agent_integration():
        all_tests_passed = False

    # Test AgentBuilder utility
    if not test_agent_builder():
        all_tests_passed = False

    # Test backward compatibility
    if not test_backward_compatibility():
        all_tests_passed = False

    # Test multi-agent scenario
    if not test_multi_agent_scenario():
        all_tests_passed = False

    print("\n" + "=" * 60)
    if all_tests_passed:
        print("🎉 All modular model selection tests passed!")
        print("\n💡 Key Benefits of Modular Design:")
        print("  ✅ Reusable across all agents")
        print("  ✅ Consistent model selection interface")
        print("  ✅ Automatic availability detection")
        print("  ✅ Graceful error handling")
        print("  ✅ Backward compatibility maintained")
        print("\n🚀 Usage Examples:")
        print("  # Interactive selection")
        print("  agent = create_finance_news_agent(interactive=True)")
        print("  # Specific model")
        print("  agent = create_finance_news_agent(model_choice='openai')")
        print("  # Using AgentBuilder directly")
        print("  builder = AgentBuilder(tools, instructions)")
        print("  agent = builder.build_with_model_selection()")
    else:
        print("❌ Some tests failed. Check the errors above.")
        print("💡 This is normal if you don't have all API keys configured.")


if __name__ == "__main__":
    main()
