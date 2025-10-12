#!/usr/bin/env python3
"""
News Agent Launcher - Easy access to all news agent functionality
Handles import paths automatically for the organized structure
"""

import os
from pathlib import Path
import sys

# Set up paths for organized structure
current_dir = Path(__file__).parent.parent  # Go up to /src/
project_root = current_dir.parent  # Go up to project root
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(current_dir / "agents"))
sys.path.insert(0, str(current_dir / "utils"))
sys.path.insert(0, str(current_dir / "core"))

from dotenv import load_dotenv

# Load environment variables
load_dotenv(project_root / "config" / ".env")  # Load from config folder
load_dotenv()  # Also check root for .env


def main():
    """Main launcher interface"""
    print("🚀 News Agent Launcher")
    print("=" * 50)

    # Check API key
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY is required!")
        print("📁 Copy config/.env.example to .env and add your API key")
        return

    print("🎯 Choose what to run:")
    print()
    print("📰 General News Agents:")
    print("  1. Interactive News Demo")
    print("  2. Simple Usage Examples")
    print("  3. Comprehensive Report Examples")
    print()
    print("🚀 GitHub Trending:")
    print("  4. GitHub Trending Agent")
    print("  5. GitHub Trending Reporter")
    print("  6. Test GitHub Functionality")
    print()
    print("💰 Financial Markets:")
    print("  7. Finance News & Market Analysis Agent")
    print()
    print("🌟 Combined Analysis:")
    print("  8. Tech News Hub (News + GitHub)")
    print()
    print("⚙️ Utilities:")
    print("  9. Quick Report Generation")
    print("  10. Project Structure Info")

    try:
        choice = input("\nEnter your choice (1-10): ").strip()

        if choice == "1":
            print("\n🚀 Starting Interactive News Demo...")
            from examples.run_news_demo import main as demo_main

            demo_main()

        elif choice == "2":
            print("\n🚀 Starting Simple Examples...")
            from examples.simple_example import main as simple_main

            simple_main()

        elif choice == "3":
            print("\n🚀 Starting Comprehensive Examples...")
            from examples.save_reports_example import main as save_main

            save_main()

        elif choice == "4":
            print("\n🚀 Starting GitHub Trending Agent...")
            from agents.github_trending_agent import main as github_main

            github_main()

        elif choice == "5":
            print("\n🚀 Starting GitHub Trending Reporter...")
            from utils.github_trending_reporter import main as reporter_main

            reporter_main()

        elif choice == "6":
            print("\n🚀 Testing GitHub Functionality...")
            from examples.test_github_trending import main as test_main

            test_main()

        elif choice == "7":
            print("\n💰 Starting Finance News & Market Analysis Agent...")
            print("💡 This agent supports multiple AI models (Claude, OpenAI, Gemini)")
            from agents.finance_news_agent import main as finance_main

            finance_main()

        elif choice == "8":
            print("\n🚀 Starting Tech News Hub...")
            from agents.tech_news_hub import main as hub_main

            hub_main()

        elif choice == "9":
            print("\n🚀 Quick Report Generation...")
            query = input("Enter your news query: ").strip()
            if query:
                from utils.report_utils import quick_news_report

                filepath = quick_news_report(query)
                print(f"✅ Report generated: {filepath}")
            else:
                print("❌ No query provided")

        elif choice == "10":
            print("\n📁 Project Structure:")
            structure_file = news_root / "PROJECT_STRUCTURE.md"
            if structure_file.exists():
                with open(structure_file) as f:
                    print(f.read()[:1000] + "...")
                print(f"\n📖 Full structure documentation: {structure_file}")
            else:
                print("Structure file not found")

        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n👋 Launcher exited")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("💡 Try running components directly from their respective folders")


if __name__ == "__main__":
    main()
