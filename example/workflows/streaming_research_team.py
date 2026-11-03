from typing import Iterator

from agno.agent import Agent
from agno.tools.duckduckgo import DuckDuckGoTools
from agno.tools.yfinance import YFinanceTools
from agno.workflow import Condition, Step, Workflow, StepInput
from agno.run.workflow import WorkflowRunOutput, WorkflowRunOutputEvent, WorkflowRunEvent
from agno.models.openrouter import OpenRouter
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
if os.path.exists('.env'):
    load_dotenv()



model_id="x-ai/grok-4.1-fast:free"
# === BASIC AGENTS ===
researcher = Agent(
    name="Researcher",
    model=OpenRouter(id=model_id),
    markdown=True,    
    instructions="Research the given topic and provide detailed findings.",
    tools=[YFinanceTools()],
)

summarizer = Agent(
    name="Summarizer",
    model=OpenRouter(id=model_id),
    markdown=True,    
    instructions="Create a clear summary of the research findings.",
)

fact_checker = Agent(
    name="Fact Checker",
    model=OpenRouter(id=model_id),
    markdown=True,    
    instructions="Verify facts and check for accuracy in the research.",
    tools=[DuckDuckGoTools()],
)

writer = Agent(
    name="Writer",
    model=OpenRouter(id=model_id),
    markdown=True,        
    instructions="Write a comprehensive article based on all available research and verification.",
)

# === CONDITION EVALUATOR ===
def needs_fact_checking(step_input: StepInput) -> bool:
    """Determine if the research contains claims that need fact-checking"""
    summary = step_input.previous_step_content or ""

    # Look for keywords that suggest factual claims
    fact_indicators = [
        "study shows",
        "breakthroughs",
        "research indicates",
        "according to",
        "statistics",
        "data shows",
        "survey",
        "report",
        "million",
        "billion",
        "percent",
        "%",
        "increase",
        "decrease",
    ]

    return any(indicator in summary.lower() for indicator in fact_indicators)


# === WORKFLOW STEPS ===
research_step = Step(
    name="research",
    description="Research the topic",
    agent=researcher,
)

summarize_step = Step(
    name="summarize",
    description="Summarize research findings",
    agent=summarizer,
)

# Conditional fact-checking step
fact_check_step = Step(
    name="fact_check",
    description="Verify facts and claims",
    agent=fact_checker,
)

write_article = Step(
    name="write_article",
    description="Write final article",
    agent=writer,
)

# === BASIC LINEAR WORKFLOW ===
basic_workflow = Workflow(
    name="Basic Linear Workflow",
    description="Research -> Summarize -> Condition(Fact Check) -> Write Article",
    steps=[
        research_step,
        summarize_step,
        Condition(
            name="fact_check_condition",
            description="Check if fact-checking is needed",
            evaluator=needs_fact_checking,
            steps=[fact_check_step],
        ),
        write_article,
    ],
    debug_mode=True,
)

if __name__ == "__main__":
    try:
        response: Iterator[WorkflowRunOutputEvent] = basic_workflow.run(
            input="Recent earning events from Nvidia and what impact to the stock market",
            stream=True,
            stream_events=True,
        )
        for event in response:
            if event.event == WorkflowRunEvent.condition_execution_started.value:
                print(event)
                print()
            elif event.event == WorkflowRunEvent.condition_execution_completed.value:
                print(event)
                print()
            elif event.event == WorkflowRunEvent.workflow_started.value:
                print(event)
                print()
            elif event.event == WorkflowRunEvent.step_started.value:
                print(event)
                print()
            elif event.event == WorkflowRunEvent.step_completed.value:
                print(event)
                print()
            elif event.event == WorkflowRunEvent.workflow_completed.value:
                print(event)
                print()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback

        traceback.print_exc()