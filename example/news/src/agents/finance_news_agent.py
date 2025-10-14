#!/usr/bin/env python3
"""
Finance News Agent
Specialized agent for financial markets, stocks, crypto, and economic news
"""

# Standard library imports
from datetime import datetime
import os
from pathlib import Path
import re
import sys

# Add paths for imports from organized structure - must be before third-party imports
current_dir = Path(__file__).parent
news_root = current_dir.parent
sys.path.insert(0, str(news_root))
sys.path.insert(0, str(current_dir))
sys.path.insert(0, str(news_root / "utils"))

# Third-party imports
from dotenv import load_dotenv  # noqa: E402

# Local imports - require path setup above
from model_selector import AgentBuilder  # noqa: E402
from report_utils import save_agent_response_to_md  # noqa: E402
from prompts.finance_news_prompt import get_finance_news_instructions  # noqa: E402
from tools.finance_tools import build_finance_tools  # noqa: E402

# Load environment variables
load_dotenv()


def create_finance_news_agent(model_choice="openai", interactive=False):
    """Create a specialized finance news agent with comprehensive market coverage."""

    current_date = datetime.now().strftime("%B %d, %Y")
    current_year = datetime.now().year

    tools = build_finance_tools()
    instructions = get_finance_news_instructions(
        current_date=current_date,
        current_year=current_year,
    )

    builder = AgentBuilder(
        tools=tools,
        instructions=instructions,
        markdown=True,
        enable_session_summaries=True,
    )

    if interactive or model_choice.lower() == "interactive":
        return builder.build_with_model_selection(
            title="Choose AI Model for Finance Agent", show_descriptions=True
        )

    return builder.build_with_model_name(model_choice)


def main():
    """Interactive finance news agent with report saving capabilities"""
    print("💰 Finance News & Market Analysis Agent")
    print("=" * 50)

    # Ensure reports directory exists
    reports_dir = news_root / "reports"
    reports_dir.mkdir(exist_ok=True)

    # Create finance agent with interactive model selection
    print("🔧 Creating specialized finance agent...")
    try:
        agent = create_finance_news_agent(interactive=True)
        print("✅ Finance agent created successfully!")
    except Exception as e:
        print(f"❌ Failed to create finance agent: {e}")
        return

    print("\n💡 Finance Agent Capabilities:")
    print("📊 Market Overview - Get real-time market indices and performance")
    print("📈 Stock Analysis - Detailed company analysis with fundamentals")
    print("🪙 Crypto Markets - Cryptocurrency overview and trends")
    print("🏭 Sector Performance - Industry sector analysis and rotation")
    print("📰 Financial News - Latest market news and analysis")

    print("\n🎯 Example queries:")
    queries = [
        "What's the current market overview?",
        "Analyze AAPL stock with recent news",
        "Show me cryptocurrency market trends",
        "What are the best performing sectors today?",
        "Find news about Federal Reserve policy",
        "How are tech stocks performing this week?",
        "Get analysis on SPY and QQQ trends",
    ]

    for i, query in enumerate(queries, 1):
        print(f"  {i}. {query}")

    # Interactive mode
    print("\n" + "=" * 50)
    print("💡 Ask about stocks, markets, crypto, economic news, or sector analysis!")
    print("Examples:")
    print("  - 'market overview'")
    print("  - 'analyze TSLA with latest news'")
    print("  - 'crypto market trends'")
    print("  - 'technology sector performance'")
    print("\n💾 Options:")
    print("  - Type 'save' after any query to save the last response to markdown")
    print("  - Or use 'save <filename>' to specify a custom filename")

    last_response = None
    last_query = None

    while True:
        try:
            user_input = input("\n💰 Your financial query (or 'quit' to exit): ").strip()

            if user_input.lower() in ["quit", "exit", "q"]:
                print("💰 Happy investing! (This is not financial advice)")
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
                    safe_query = re.sub(r"[^\w\s-]", "", last_query).strip()
                    safe_query = re.sub(r"[-\s]+", "_", safe_query)
                    filename = f"finance_report_{safe_query[:30]}"

                try:
                    filepath = save_agent_response_to_md(
                        agent=agent,
                        query=last_query,
                        filename=filename,
                        title=f"Finance Report: {last_query}",
                        reports_dir=str(reports_dir),
                        response_content=last_response,
                    )
                    print(f"✅ Financial report saved: {filepath}")
                except Exception as e:
                    print(f"❌ Error saving report: {e}")
                continue

            # Process regular queries
            user_query = user_input
            print(f"\n📊 Analyzing: {user_query}")
            print("-" * 40)

            response = agent.run(user_query)
            print(response.content)

            # Store for potential saving
            last_response = response.content
            last_query = user_query

            print("\n💡 Type 'save' to save this financial analysis to reports/")

        except KeyboardInterrupt:
            print("\n💰 Happy investing! (This is not financial advice)")
            break
        except EOFError:
            print("\n💰 Happy investing! (This is not financial advice)")
            break
        except Exception as e:
            print(f"❌ Error: {e}")
            continue


if __name__ == "__main__":
    main()
