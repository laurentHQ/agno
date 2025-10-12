import random

from agno.agent import Agent
from agno.models.openai import OpenAIChat
from agno.tools import tool

# This is our tool, marked by the @tool decorator
@tool(stop_after_tool_call=True)
def get_weather(city: str) -> str:
    """Get the weather for the given city."""

    # In a real implementation, this would call a weather API
    weather_conditions = ["sunny", "cloudy", "rainy", "snowy", "windy"]
    random_weather = random.choice(weather_conditions)

    return f"The weather in {city} is {random_weather}."

# To equipt our Agent with our tool, we simply pass it with the tools parameter
agent = Agent(
    model=OpenAIChat(id="gpt-5-nano"),
    tools=[get_weather],
    markdown=True,
)

# Our Agent will now be able to use our tool, when it deems it relevant
agent.print_response("What is the weather in Kuala Lumpur, Malaysia? Details please.", stream=True)