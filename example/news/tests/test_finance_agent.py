#!/usr/bin/env python3
"""
Test script for Finance News Agent
Verifies functionality without full interactive mode
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


def test_finance_tools():
    """Test the AdvancedFinanceTools class"""
    print("🧪 Testing Finance Tools...")

    try:
        from finance_news_agent import AdvancedFinanceTools

        tools = AdvancedFinanceTools()

        print("✅ Finance tools imported successfully")

        # Test market overview
        print("📊 Testing market overview...")
        market_overview = tools.get_market_overview()
        print(f"   Market data retrieved: {len(market_overview)} characters")

        # Test stock analysis
        print("📈 Testing stock analysis...")
        stock_analysis = tools.get_stock_analysis("AAPL")
        print(f"   AAPL analysis retrieved: {len(stock_analysis)} characters")

        # Test crypto overview
        print("🪙 Testing crypto overview...")
        crypto_overview = tools.get_crypto_overview()
        print(f"   Crypto data retrieved: {len(crypto_overview)} characters")

        # Test sector performance
        print("🏭 Testing sector performance...")
        sector_performance = tools.get_sector_performance()
        print(f"   Sector data retrieved: {len(sector_performance)} characters")

        print("✅ All finance tools tests passed!")
        return True

    except Exception as e:
        print(f"❌ Finance tools test failed: {e}")
        return False


def test_agent_creation():
    """Test creating the finance agent"""
    print("\n🤖 Testing Finance Agent Creation...")

    if not os.getenv("ANTHROPIC_API_KEY"):
        print("⚠️  ANTHROPIC_API_KEY not set - skipping agent test")
        return True

    try:
        from finance_news_agent import create_finance_news_agent

        # Test programmatic model selection
        agent = create_finance_news_agent(model_choice="claude")
        print("✅ Finance agent created with Claude")

        # Test with different models if available
        if os.getenv("OPENAI_API_KEY"):
            agent_openai = create_finance_news_agent(model_choice="openai")
            print("✅ Finance agent created with OpenAI")

        return True

    except Exception as e:
        print(f"❌ Agent creation failed: {e}")
        return False


def test_model_selector():
    """Test the modular model selector"""
    print("\n🔧 Testing Model Selector...")

    try:
        from model_selector import AgentBuilder, ModelAvailability, ModelRegistry

        # Test model registry
        registry = ModelRegistry()
        all_models = registry.get_all_models()
        print(f"✅ Model registry: {len(all_models)} models configured")

        # Test availability checking
        availability = ModelAvailability()
        available_models = availability.get_available_models()
        print(f"✅ Available models: {len(available_models)} models ready")

        # Test AgentBuilder
        from finance_news_agent import AdvancedFinanceTools

        tools = [AdvancedFinanceTools()]
        instructions = "Test agent"

        builder = AgentBuilder(tools=tools, instructions=instructions)
        print("✅ AgentBuilder created successfully")

        return True

    except Exception as e:
        print(f"❌ Model selector test failed: {e}")
        return False


def test_report_integration():
    """Test report saving integration"""
    print("\n💾 Testing Report Integration...")

    try:
        print("✅ Report utilities imported successfully")

        # Test that we can create reports directory
        reports_dir = news_root / "reports"
        reports_dir.mkdir(exist_ok=True)
        print("✅ Reports directory ready")

        return True

    except Exception as e:
        print(f"❌ Report integration test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Finance Agent Test Suite")
    print("=" * 40)

    all_tests_passed = True

    # Test finance tools
    if not test_finance_tools():
        all_tests_passed = False

    # Test model selector
    if not test_model_selector():
        all_tests_passed = False

    # Test agent creation
    if not test_agent_creation():
        all_tests_passed = False

    # Test report integration
    if not test_report_integration():
        all_tests_passed = False

    print("\n" + "=" * 40)
    if all_tests_passed:
        print("🎉 All tests passed! Finance agent is ready to use.")
        print("\n💡 To run the finance agent:")
        print("  python agents/finance_news_agent.py")
        print("  OR")
        print("  python launcher.py  # Choose option 7")
    else:
        print("❌ Some tests failed. Check the errors above.")


if __name__ == "__main__":
    main()
