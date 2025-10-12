#!/usr/bin/env python3
"""
Test script for GitHub Trending functionality
"""

import os
from pathlib import Path
import sys

# Add current directory to path for imports
current_dir = Path(__file__).parent
sys.path.insert(0, str(current_dir))

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_github_api():
    """Test GitHub API connection"""
    print("🔧 Testing GitHub API connection...")

    try:
        from github_trending_agent import GitHubTrendingTools

        tools = GitHubTrendingTools()
        result = tools.get_trending_repos(limit=3)

        print("✅ GitHub API connection successful!")
        print("📋 Sample trending repositories:")
        print(result[:500] + "..." if len(result) > 500 else result)

    except Exception as e:
        print(f"❌ GitHub API test failed: {e}")
        print("💡 This is normal if you don't have internet connection")


def test_github_agent():
    """Test GitHub trending agent"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY required for agent testing")
        return

    print("\n🤖 Testing GitHub trending agent...")

    try:
        from github_trending_agent import create_github_trending_agent

        agent = create_github_trending_agent(language="python")
        print("✅ GitHub trending agent created successfully!")

        # Test query
        print("🔍 Testing with sample query...")
        response = agent.run("Show me the top 3 trending Python repositories")

        print("✅ Agent response received!")
        print("📄 Sample response:")
        print(response.content[:300] + "..." if len(response.content) > 300 else response.content)

    except Exception as e:
        print(f"❌ GitHub agent test failed: {e}")


def test_tech_news_hub():
    """Test tech news hub integration"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY required for hub testing")
        return

    print("\n🌟 Testing Tech News Hub...")

    try:
        from tech_news_hub import TechNewsHub

        hub = TechNewsHub()
        print("✅ Tech News Hub created successfully!")

        # You could uncomment this to test report generation:
        # print("📊 Generating sample AI report...")
        # filepath = hub.generate_ai_focus_report()
        # print(f"✅ Report generated: {filepath}")

    except Exception as e:
        print(f"❌ Tech News Hub test failed: {e}")


def main():
    """Run all tests"""
    print("🧪 GitHub Trending News Agent - Test Suite")
    print("=" * 50)

    # Test 1: GitHub API
    test_github_api()

    # Test 2: GitHub Agent
    test_github_agent()

    # Test 3: Tech News Hub
    test_tech_news_hub()

    print("\n" + "=" * 50)
    print("🎉 Test suite completed!")
    print("\n💡 To generate actual reports:")
    print("  python github_trending_agent.py")
    print("  python github_trending_reporter.py")
    print("  python tech_news_hub.py")


if __name__ == "__main__":
    main()
