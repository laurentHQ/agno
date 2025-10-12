#!/usr/bin/env python3
"""
Demo script for the Multi-Source News Agent
Shows different usage patterns and capabilities
"""

import os
from pathlib import Path
import sys

# Add paths for imports from organized structure
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(news_root / "agents"))

from dotenv import load_dotenv

from agents.multisource_news_agent import (
    create_basic_news_agent,
    create_enhanced_news_agent,
    create_specialized_agents,
)

# Load environment variables
load_dotenv()


def demo_basic_agent():
    """Demo the basic news agent with free tools only"""
    print("🔧 Creating Basic News Agent (Free tools only)...")
    agent = create_basic_news_agent()

    print("\n📰 Getting HackerNews trending stories...")
    response = agent.run("What are the top trending stories on HackerNews today?")
    print(response.content)


def demo_enhanced_agent():
    """Demo the enhanced news agent with all available tools"""
    print("🔧 Creating Enhanced Multi-Source News Agent...")
    agent = create_enhanced_news_agent()

    queries = [
        "What are the latest AI developments in the news?",
        "Give me a comprehensive tech news summary from multiple sources",
        "What's trending in the startup world today?",
    ]

    for query in queries:
        print(f"\n🔍 Query: {query}")
        print("-" * 60)
        response = agent.run(query)
        print(response.content)
        print("\n" + "=" * 60)


def demo_specialized_agents():
    """Demo specialized agents for different news categories"""
    print("🔧 Creating Specialized News Agents...")
    agents = create_specialized_agents()

    # Tech news
    print("\n💻 Tech News Agent:")
    print("-" * 30)
    tech_response = agents["tech"].run("What are the latest tech breakthroughs and startup news?")
    print(tech_response.content)

    # Financial news
    print("\n💰 Financial News Agent:")
    print("-" * 30)
    finance_response = agents["finance"].run(
        "What are the major market movements and financial news today?"
    )
    print(finance_response.content)


def check_environment():
    """Check which API keys are available"""
    print("🔍 Checking Environment Configuration...")
    print("=" * 50)

    required_keys = ["ANTHROPIC_API_KEY"]
    optional_keys = [
        "REDDIT_CLIENT_ID",
        "REDDIT_CLIENT_SECRET",
        "TAVILY_API_KEY",
        "GOOGLE_API_KEY",
        "BRAVE_API_KEY",
        "FIRECRAWL_API_KEY",
    ]

    print("✅ Required API Keys:")
    for key in required_keys:
        status = "✓ Set" if os.getenv(key) else "✗ Missing"
        print(f"   {key}: {status}")

    print("\n🔧 Optional API Keys (for enhanced features):")
    for key in optional_keys:
        status = "✓ Set" if os.getenv(key) else "✗ Not set"
        print(f"   {key}: {status}")

    print("\n💡 Note: The agent will work with just ANTHROPIC_API_KEY using free tools.")
    print("   Additional API keys unlock more news sources and features.")


if __name__ == "__main__":
    print("🚀 Multi-Source News Agent Demo")
    print("=" * 50)

    # Check environment
    check_environment()

    # Check if basic requirements are met
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("\n❌ ANTHROPIC_API_KEY is required!")
        print("Please set it in your .env file or environment variables.")
        exit(1)

    print("\n" + "=" * 50)
    print("🎯 Choose a demo mode:")
    print("1. Basic Agent (Free tools only - HackerNews, DuckDuckGo, Newspaper)")
    print("2. Enhanced Agent (All available tools)")
    print("3. Specialized Agents (Tech & Finance focused)")
    print("4. Interactive Mode")

    try:
        choice = input("\nEnter your choice (1-4): ").strip()

        if choice == "1":
            demo_basic_agent()
        elif choice == "2":
            demo_enhanced_agent()
        elif choice == "3":
            demo_specialized_agents()
        elif choice == "4":
            print("\n🚀 Starting Interactive Mode...")
            agent = create_enhanced_news_agent()

            print("Type your news queries below (type 'quit' to exit):")
            while True:
                query = input("\n📰 News query: ").strip()
                if query.lower() in ["quit", "exit", "q"]:
                    break
                if query:
                    print(f"\n🔍 Searching: {query}")
                    print("-" * 40)
                    response = agent.run(query)
                    print(response.content)
        else:
            print("Invalid choice. Please run the script again.")

    except KeyboardInterrupt:
        print("\n👋 Demo interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Error: {e}")

    print("\n👋 Demo completed!")
