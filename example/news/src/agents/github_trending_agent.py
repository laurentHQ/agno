#!/usr/bin/env python3
"""
GitHub Trending Repository News Agent
Searches for trending GitHub repositories and related news
"""

from datetime import datetime
import os
from pathlib import Path
import sys

import requests

# Add paths for imports from organized structure
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(news_root / "utils"))

from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools import Toolkit
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.hackernews import HackerNewsTools
from agno.tools.reddit import RedditTools
from dotenv import load_dotenv

# Import report utilities
from report_utils import save_agent_response_to_md

# Load environment variables
load_dotenv()


class GitHubTrendingTools(Toolkit):
    """Custom toolkit for GitHub trending repositories"""

    def __init__(self, language: str = None, since: str = "daily"):
        """
        Initialize GitHub Trending Tools

        Args:
            language: Programming language filter (e.g., 'python', 'javascript')
            since: Time period ('daily', 'weekly', 'monthly')
        """
        super().__init__()
        self.language = language
        self.since = since

    def get_trending_repos(self, language: str = None, since: str = None, limit: int = 10) -> str:
        """
        Get trending GitHub repositories

        Args:
            language: Programming language to filter by
            since: Time period for trending ('daily', 'weekly', 'monthly')
            limit: Number of repositories to return

        Returns:
            Formatted string with trending repositories information
        """
        try:
            # Use provided parameters or fall back to instance defaults
            lang = language or self.language
            period = since or self.since

            # GitHub API endpoint for searching repositories
            base_url = "https://api.github.com/search/repositories"

            # Calculate date for trending query
            from datetime import datetime, timedelta

            if period == "daily":
                date_threshold = datetime.now() - timedelta(days=1)
            elif period == "weekly":
                date_threshold = datetime.now() - timedelta(days=7)
            elif period == "monthly":
                date_threshold = datetime.now() - timedelta(days=30)
            else:
                date_threshold = datetime.now() - timedelta(days=1)

            date_str = date_threshold.strftime("%Y-%m-%d")

            # Build query
            query_parts = [f"created:>{date_str}"]
            if lang:
                query_parts.append(f"language:{lang}")

            query = " ".join(query_parts)

            params = {"q": query, "sort": "stars", "order": "desc", "per_page": str(limit)}

            # Add GitHub token if available
            headers = {}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            response = requests.get(base_url, params=params, headers=headers)
            response.raise_for_status()

            data = response.json()
            repos = data.get("items", [])

            if not repos:
                return f"No trending repositories found for {lang or 'all languages'} in the {period} period."

            # Format results
            result = f"## Trending GitHub Repositories ({period.title()})\n\n"
            if lang:
                result += f"**Language:** {lang.title()}\n\n"

            for i, repo in enumerate(repos, 1):
                result += f"### {i}. {repo['name']}\n"
                result += f"**Owner:** {repo['owner']['login']}\n"
                result += f"**Description:** {repo.get('description', 'No description')}\n"
                result += f"**Stars:** ⭐ {repo['stargazers_count']:,}\n"
                result += f"**Language:** {repo.get('language', 'Not specified')}\n"
                result += f"**URL:** {repo['html_url']}\n"
                result += f"**Created:** {repo['created_at'][:10]}\n"
                result += f"**Last Updated:** {repo['updated_at'][:10]}\n"

                if repo.get("topics"):
                    result += f"**Topics:** {', '.join(repo['topics'])}\n"

                result += "\n---\n\n"

            return result

        except Exception as e:
            return f"Error fetching trending repositories: {e!s}"

    def search_repo_news(self, repo_name: str, owner: str = None) -> str:
        """
        Search for news about a specific repository

        Args:
            repo_name: Name of the repository
            owner: Owner/organization name

        Returns:
            Search query for news about the repository
        """
        if owner:
            search_term = f"{owner}/{repo_name}"
        else:
            search_term = repo_name

        return f"GitHub repository {search_term} news updates discussions"

    def get_repo_stats(self, owner: str, repo: str) -> str:
        """
        Get detailed statistics for a specific repository

        Args:
            owner: Repository owner
            repo: Repository name

        Returns:
            Formatted repository statistics
        """
        try:
            url = f"https://api.github.com/repos/{owner}/{repo}"

            headers = {}
            github_token = os.getenv("GITHUB_TOKEN")
            if github_token:
                headers["Authorization"] = f"token {github_token}"

            response = requests.get(url, headers=headers)
            response.raise_for_status()

            data = response.json()

            result = f"## Repository Statistics: {owner}/{repo}\n\n"
            result += f"**Description:** {data.get('description', 'No description')}\n"
            result += f"**Language:** {data.get('language', 'Not specified')}\n"
            result += f"**Stars:** ⭐ {data['stargazers_count']:,}\n"
            result += f"**Forks:** 🍴 {data['forks_count']:,}\n"
            result += f"**Watchers:** 👀 {data['watchers_count']:,}\n"
            result += f"**Open Issues:** 🐛 {data['open_issues_count']:,}\n"
            result += f"**Size:** {data['size']:,} KB\n"
            result += f"**Created:** {data['created_at'][:10]}\n"
            result += f"**Last Updated:** {data['updated_at'][:10]}\n"
            result += f"**Last Push:** {data['pushed_at'][:10]}\n"
            result += f"**Default Branch:** {data['default_branch']}\n"
            result += f"**License:** {data.get('license', {}).get('name', 'Not specified')}\n"
            result += f"**URL:** {data['html_url']}\n"

            if data.get("topics"):
                result += f"**Topics:** {', '.join(data['topics'])}\n"

            if data.get("homepage"):
                result += f"**Homepage:** {data['homepage']}\n"

            return result

        except Exception as e:
            return f"Error fetching repository statistics: {e!s}"


def create_github_trending_agent(language: str = None, include_news: bool = True):
    """
    Create an agent specialized in GitHub trending repositories and related news

    Args:
        language: Programming language to focus on
        include_news: Whether to include news search capabilities

    Returns:
        Configured Agno agent
    """
    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    # Core tools
    tools = [GitHubTrendingTools(language=language)]

    # Add news search tools if requested
    if include_news:
        tools.extend(
            [
                HackerNewsTools(),
                DuckDuckGoTools(enable_search=True, enable_news=True),
            ]
        )

        # Add Reddit if API keys available
        if os.getenv("REDDIT_CLIENT_ID") and os.getenv("REDDIT_CLIENT_SECRET"):
            tools.append(RedditTools())

    # Build instructions
    lang_context = f" focusing on {language}" if language else ""
    instructions = f"""
    You are a GitHub trending repository specialist{lang_context}.

    **CURRENT CONTEXT:**
    - Today's date: {current_date}
    - Current year: {current_year}
    - Focus on {current_year} repositories and developments

    **Your Capabilities:**
    1. **Repository Discovery**: Find trending GitHub repositories by language, timeframe, and popularity
    2. **Repository Analysis**: Get detailed statistics and information about specific repositories
    3. **News Integration**: Search for news, discussions, and community sentiment about repositories
    4. **Trend Analysis**: Identify patterns in repository popularity and development activity

    **When asked about trending repositories:**
    1. Use get_trending_repos() to find current trending repositories
    2. Use get_repo_stats() for detailed information about specific repositories
    3. Search for related news and discussions using DuckDuckGo and HackerNews
    4. Check Reddit for community discussions and developer sentiment
    5. Provide context about why repositories are trending

    **Response Guidelines:**
    1. Always include repository statistics (stars, forks, issues)
    2. Explain what makes each repository interesting or noteworthy
    3. Include links to repositories and related resources
    4. Mention the programming language and key technologies
    5. Highlight recent updates, releases, or significant changes
    6. Include community sentiment and developer discussions when available

    **For repository analysis:**
    - Focus on code quality indicators (documentation, tests, maintenance)
    - Highlight innovative features or approaches
    - Mention potential use cases and target audience
    - Include information about contributors and community activity
    """

    return Agent(
        model=Claude(id="claude-sonnet-4-5"),
        tools=tools,
        instructions=instructions,
        markdown=True,
    )


def main():
    """Interactive GitHub trending repository explorer"""
    if not os.getenv("ANTHROPIC_API_KEY"):
        print("❌ ANTHROPIC_API_KEY is required!")
        return

    print("🚀 GitHub Trending Repository News Agent")
    print("=" * 50)

    # Ensure reports directory exists
    reports_dir = news_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Language selection
    print("Choose a programming language focus (or press Enter for all):")
    popular_languages = [
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

    for i, lang in enumerate(popular_languages, 1):
        print(f"  {i:2d}. {lang.title()}")

    choice = input("\nEnter number or language name (or Enter for all): ").strip()

    language = None
    if choice.isdigit() and 1 <= int(choice) <= len(popular_languages):
        language = popular_languages[int(choice) - 1]
    elif choice.lower() in popular_languages or choice:
        language = choice.lower()

    # Create agent
    print(f"\n🔧 Creating GitHub trending agent{f' for {language}' if language else ''}...")
    agent = create_github_trending_agent(language=language)

    print("\n🎯 Example queries:")
    queries = [
        "What are the trending repositories today?",
        "Show me trending Python repositories this week",
        "Find trending AI/ML repositories and related news",
        "What's popular in the JavaScript ecosystem lately?",
        "Show me trending repositories with recent news coverage",
    ]

    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Interactive mode
    print("\n" + "=" * 50)
    print("💡 Ask about trending repositories, specific repos, or related news!")
    print("Examples:")
    print("  - 'trending repositories today'")
    print("  - 'trending python repos this week'")
    print("  - 'tell me about microsoft/vscode repository'")
    print("  - 'AI repositories trending with news'")
    print("\n💾 Options:")
    print("  - Type 'save' after any query to save the last response to markdown")
    print("  - Or use 'save <filename>' to specify a custom filename")

    last_response = None
    last_query = None

    while True:
        try:
            user_input = input("\n🔍 Your query (or 'quit' to exit): ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("👋 Happy coding!")
                break

            if not user_input:
                continue

            # Handle save commands
            if user_input.lower().startswith("save"):
                if not last_response or not last_query:
                    print("❌ No previous response to save. Run a query first.")
                    continue

                # Extract filename if provided
                parts = user_input.split(maxsplit=1)
                if len(parts) > 1:
                    filename = parts[1]
                else:
                    # Generate filename from query
                    import re

                    safe_query = re.sub(r"[^\w\s-]", "", last_query).strip()
                    safe_query = re.sub(r"[-\s]+", "_", safe_query)
                    filename = f"github_trending_{safe_query[:30]}"

                try:
                    filepath = save_agent_response_to_md(
                        agent=agent,
                        query=last_query,
                        filename=filename,
                        title=f"GitHub Trending Report: {last_query}",
                        reports_dir=str(reports_dir),
                        response_content=last_response,
                    )
                    print(f"✅ Report saved: {filepath}")
                except Exception as e:
                    print(f"❌ Error saving report: {e}")
                continue

            # Process regular queries
            user_query = user_input
            print(f"\n🔍 Searching: {user_query}")
            print("-" * 40)

            response = agent.run(user_query)
            print(response.content)

            # Store for potential saving
            last_response = response.content
            last_query = user_query

            print("\n💡 Type 'save' to save this response to reports/")

        except KeyboardInterrupt:
            print("\n👋 Happy coding!")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
