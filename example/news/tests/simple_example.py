#!/usr/bin/env python3
"""
Simple example showing how to save agent responses to markdown files
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

from agents.multisource_news_agent import create_enhanced_news_agent
from utils.report_utils import quick_news_report, save_agent_response_to_md

# Load environment variables
load_dotenv()


def main():
    # Check if API key is set
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ Please set ANTHROPIC_API_KEY in your .env file")
        return
    # ask for which method to use
    print("Which method to use?")
    print("1. Quick Report Generation")
    print("2. Custom Agent with Utility")
    print("3. Multiple Reports")
    choice = input("Enter your choice: ")

    print("🚀 Simple News Report Generation Example")
    print("=" * 50)

    # Method 1: Using the utility function (easiest)
    if choice == "1":
        print("Method 1: Quick Report Generation")
        filepath = quick_news_report(
            query="What are the latest developments in AI technology?",
            filename="ai_developments_report",
        )
        print(f"✅ Saved to: {filepath}\n")

    # Method 2: Using agent directly with utility function
    elif choice == "2":
        print("Method 2: Custom Agent with Utility")
        agent = create_enhanced_news_agent()

        filepath = save_agent_response_to_md(
            agent=agent,
            query="Give me a summary of today's startup and business news",
            filename="startup_news_summary",
            title="Daily Startup News Summary",
        )
        print(f"✅ Saved to: {filepath}\n")

    # Method 3: Multiple queries in a loop
    elif choice == "3":
        print("Method 3: Multiple Reports")
        queries = [
            "What's happening in the cryptocurrency market?",
            "Show me the latest tech industry mergers and acquisitions",
            "Give me updates on renewable energy and climate tech news",
        ]

        for i, query in enumerate(queries, 1):
            print(f"Generating report {i}/3...")
            filepath = save_agent_response_to_md(
                agent=agent, query=query, title=f"News Report #{i}"
            )
            print(f"   Saved to: {filepath}")

        print("\n🎉 All reports generated successfully!")
        print("📁 Check the 'reports/' folder for your markdown files")

    else:
        print("Invalid choice")
        return


if __name__ == "__main__":
    main()
