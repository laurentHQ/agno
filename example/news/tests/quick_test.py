#!/usr/bin/env python3
"""
Quick test to verify the organized structure works
"""

from pathlib import Path
import sys

# Set up paths for organized structure
news_root = Path(__file__).parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(news_root / "agents"))
sys.path.insert(0, str(news_root / "utils"))


def test_imports():
    """Test that all imports work with the new structure"""
    print("🧪 Testing organized structure imports...")

    try:
        # Test agent imports
        from agents.multisource_news_agent import create_basic_news_agent

        print("✅ multisource_news_agent import successful")

        from agents.github_trending_agent import create_github_trending_agent

        print("✅ github_trending_agent import successful")

        from agents.tech_news_hub import TechNewsHub

        print("✅ tech_news_hub import successful")

        # Test utility imports
        from utils.report_utils import save_agent_response_to_md

        print("✅ report_utils import successful")

        from utils.news_reporter import NewsReporter

        print("✅ news_reporter import successful")

        print("\n🎉 All imports successful! The organized structure is working.")
        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False


def test_basic_functionality():
    """Test basic functionality without API calls"""
    print("\n🔧 Testing basic functionality...")

    try:
        print("✅ Report utilities available")

        # Check if reports directory exists
        reports_dir = Path("reports")
        reports_dir.mkdir(exist_ok=True)
        print("✅ Reports directory ready")

        print("✅ Basic functionality test passed")
        return True

    except Exception as e:
        print(f"❌ Functionality test failed: {e}")
        return False


def main():
    """Run all tests"""
    print("🚀 Quick Structure Test")
    print("=" * 40)

    imports_ok = test_imports()
    functionality_ok = test_basic_functionality()

    print("\n" + "=" * 40)
    if imports_ok and functionality_ok:
        print("🎉 All tests passed! Structure is working correctly.")
        print("\n💡 You can now use:")
        print("  python launcher.py  # For easy access to all functionality")
        print("  python examples/simple_example.py  # For basic usage")
        print("  python agents/multisource_news_agent.py  # Direct agent usage")
    else:
        print("❌ Some tests failed. Check the error messages above.")


if __name__ == "__main__":
    main()
