#!/usr/bin/env python3
"""
GitHub Trending Repository Reporter
Generates reports on trending GitHub repositories and saves them as markdown
"""

from datetime import datetime
import os
from pathlib import Path
import sys

# Add current directory to path for imports
current_dir = Path(__file__).parent.parent  # Go up to /src/
project_root = current_dir.parent  # Go up to project root
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(current_dir))

from dotenv import load_dotenv

from src.agents.github_trending_agent import create_github_trending_agent

from .report_utils import save_agent_response_to_md

# Load environment variables
load_dotenv()


class GitHubTrendingReporter:
    """Reporter for GitHub trending repositories with news integration"""

    def __init__(self, reports_dir="reports"):
        self.reports_dir = Path(reports_dir)
        self.reports_dir.mkdir(exist_ok=True)

    def generate_trending_report(self, language=None, period="daily", filename=None):
        """Generate a trending repositories report"""
        agent = create_github_trending_agent(language=language)

        # Build query based on parameters
        if language and period:
            query = f"Show me trending {language} repositories from the {period} period with news and community discussions"
        elif language:
            query = f"What are the trending {language} repositories with related news?"
        elif period:
            query = f"Show me trending repositories from the {period} period"
        else:
            query = "What are the trending GitHub repositories today with news coverage?"

        # Generate filename if not provided
        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            lang_part = f"_{language}" if language else ""
            filename = f"github_trending{lang_part}_{period}_{timestamp}"

        title = "GitHub Trending Repositories Report"
        if language:
            title += f" - {language.title()}"
        if period:
            title += f" ({period.title()})"

        return save_agent_response_to_md(agent=agent, query=query, filename=filename, title=title)

    def generate_language_comparison(self, languages, filename=None):
        """Generate a comparison report across multiple languages"""
        agent = create_github_trending_agent()

        query = f"Compare trending repositories across these languages: {', '.join(languages)}. Show the most popular repositories for each language with statistics and news."

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"github_language_comparison_{timestamp}"

        title = f"GitHub Trending: Language Comparison ({', '.join(languages)})"

        return save_agent_response_to_md(agent=agent, query=query, filename=filename, title=title)

    def generate_tech_trend_report(self, tech_focus="AI", filename=None):
        """Generate a report focused on specific technology trends"""
        agent = create_github_trending_agent()

        query = f"Find trending GitHub repositories related to {tech_focus}. Include repository statistics, recent news coverage, and community discussions about these projects."

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            safe_focus = tech_focus.replace("/", "_").replace(" ", "_")
            filename = f"github_tech_trend_{safe_focus}_{timestamp}"

        title = f"GitHub {tech_focus} Technology Trends Report"

        return save_agent_response_to_md(agent=agent, query=query, filename=filename, title=title)

    def generate_weekly_digest(self, filename=None):
        """Generate a comprehensive weekly digest of trending repositories"""
        agent = create_github_trending_agent()

        query = """Generate a comprehensive weekly digest of trending GitHub repositories including:
        1. Top trending repositories across all languages
        2. Most significant new projects launched this week
        3. Repositories with major updates or releases
        4. Community discussions and news coverage
        5. Emerging technology trends
        6. Notable contributor activities and achievements"""

        if not filename:
            timestamp = datetime.now().strftime("%Y%m%d")
            filename = f"github_weekly_digest_{timestamp}"

        title = f"GitHub Weekly Digest - {datetime.now().strftime('%B %d, %Y')}"

        return save_agent_response_to_md(agent=agent, query=query, filename=filename, title=title)


def quick_github_report(query, language=None, filename=None):
    """Quick function to generate a GitHub trending report"""
    agent = create_github_trending_agent(language=language)

    return save_agent_response_to_md(
        agent=agent, query=query, filename=filename, title="GitHub Trending Report"
    )


def main():
    """Interactive GitHub trending reporter"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY is required!")
        return

    print("📊 GitHub Trending Repository Reporter")
    print("=" * 50)

    reporter = GitHubTrendingReporter()

    print("🎯 Choose report type:")
    print("1. Trending repositories by language")
    print("2. Multi-language comparison")
    print("3. Technology-focused trends (AI, Web3, etc.)")
    print("4. Weekly digest")
    print("5. Custom query")

    try:
        choice = input("\nEnter your choice (1-5): ").strip()

        if choice == "1":
            # Language-specific trending
            languages = [
                "python",
                "javascript",
                "typescript",
                "java",
                "go",
                "rust",
                "cpp",
                "csharp",
                "php",
                "ruby",
                "swift",
                "kotlin",
            ]

            print("\nAvailable languages:")
            for i, lang in enumerate(languages, 1):
                print(f"  {i:2d}. {lang.title()}")

            lang_choice = input("\nEnter number or language name: ").strip()
            language = None

            if lang_choice.isdigit() and 1 <= int(lang_choice) <= len(languages):
                language = languages[int(lang_choice) - 1]
            elif lang_choice.lower() in languages or lang_choice:
                language = lang_choice.lower()

            period_choice = (
                input("Choose period (daily/weekly/monthly) [daily]: ").strip() or "daily"
            )

            filepath = reporter.generate_trending_report(language=language, period=period_choice)
            print(f"✅ Report generated: {filepath}")

        elif choice == "2":
            # Multi-language comparison
            print("Enter languages to compare (comma-separated):")
            print("Example: python, javascript, rust")
            languages_input = input("Languages: ").strip()

            if languages_input:
                languages = [lang.strip() for lang in languages_input.split(",")]
                filepath = reporter.generate_language_comparison(languages)
                print(f"✅ Comparison report generated: {filepath}")
            else:
                print("❌ No languages specified")

        elif choice == "3":
            # Technology-focused trends
            print("Enter technology focus:")
            print("Examples: AI, Web3, Machine Learning, DevOps, Blockchain")
            tech_focus = input("Technology: ").strip()

            if tech_focus:
                filepath = reporter.generate_tech_trend_report(tech_focus)
                print(f"✅ Tech trend report generated: {filepath}")
            else:
                print("❌ No technology specified")

        elif choice == "4":
            # Weekly digest
            filepath = reporter.generate_weekly_digest()
            print(f"✅ Weekly digest generated: {filepath}")

        elif choice == "5":
            # Custom query
            query = input("Enter your custom query: ").strip()
            language = input("Focus on specific language (optional): ").strip() or None

            if query:
                filepath = quick_github_report(query, language)
                print(f"✅ Custom report generated: {filepath}")
            else:
                print("❌ No query specified")

        else:
            print("❌ Invalid choice")

    except KeyboardInterrupt:
        print("\n👋 Report generation cancelled")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    main()
