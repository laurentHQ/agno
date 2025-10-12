from agno.agent import Agent
from agno.models.anthropic import Claude
from agno.tools.hackernews import HackerNewsTools
import os

from dotenv import load_dotenv
load_dotenv()
if not os.getenv("ANTHROPIC_API_KEY"):
    raise ValueError("ANTHROPIC_API_KEY is not set")
else:
    print("ANTHROPIC_API_KEY is set: ", os.getenv("ANTHROPIC_API_KEY")[:10] + "...")

agent = Agent(
    model=Claude(id="claude-sonnet-4-5"),
    tools=[HackerNewsTools()],
    markdown=True,
)
agent.print_response("Write a report on trending startups and products.", stream=True)