#!/usr/bin/env python3
"""
Agent Run Analysis Tool
Parses DEBUG logs from agent runs and generates concise summaries
"""

import re
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class ToolCall:
    """Represents a single tool call"""

    id: str
    name: str
    arguments: str
    duration: float = 0.0
    result: str = ""


@dataclass
class AgentRunMetrics:
    """Metrics from agent run"""

    input_tokens: int = 0
    output_tokens: int = 0
    total_tokens: int = 0
    reasoning_tokens: int = 0
    duration: float = 0.0
    tokens_per_second: float = 0.0


@dataclass
class AgentRunAnalysis:
    """Complete analysis of an agent run"""

    user_prompt: str = ""
    tool_calls: list[ToolCall] = field(default_factory=list)
    metrics: AgentRunMetrics = field(default_factory=AgentRunMetrics)
    instructions_used: list[str] = field(default_factory=list)
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


class AgentRunAnalyzer:
    """Analyzes agent run debug logs and generates summaries"""

    def __init__(self):
        self.analysis = AgentRunAnalysis()

    def parse_log(self, log_text: str) -> AgentRunAnalysis:
        """Parse debug log text and extract analysis"""
        lines = log_text.split("\n")

        for i, line in enumerate(lines):
            # Extract user prompt
            if "DEBUG" in line and "user" in line and "=" in line:
                # Next line should contain the prompt
                if i + 1 < len(lines):
                    prompt_line = lines[i + 1].strip()
                    if prompt_line.startswith("DEBUG"):
                        self.analysis.user_prompt = prompt_line.replace("DEBUG", "").strip()

            # Extract tool calls
            if "Tool Calls:" in line:
                tool_calls = self._parse_tool_calls(lines[i:])
                self.analysis.tool_calls.extend(tool_calls)

            # Extract tool results
            if "Tool call Id:" in line:
                tool_id = line.split("call_")[1].strip()
                if i + 1 < len(lines):
                    result_line = lines[i + 1].strip()
                    if result_line.startswith("DEBUG"):
                        result = result_line.replace("DEBUG", "").strip()
                        # Find matching tool call and update result
                        for tool in self.analysis.tool_calls:
                            if tool.id == f"call_{tool_id}":
                                tool.result = result
                                break

            # Extract tool duration
            if "TOOL METRICS" in line and "Duration:" in line:
                duration_match = re.search(r"Duration:\s+([\d.]+)s", line)
                if duration_match and self.analysis.tool_calls:
                    # Assign to most recent tool call without duration
                    for tool in reversed(self.analysis.tool_calls):
                        if tool.duration == 0.0:
                            tool.duration = float(duration_match.group(1))
                            break

            # Extract overall metrics
            if "METRICS" in line and "Tokens:" in line:
                self.analysis.metrics = self._parse_metrics(line)

            # Extract instructions
            if "instructions>" in line.lower() or "critical:" in line.lower():
                instruction = self._extract_instruction(line)
                if instruction and instruction not in self.analysis.instructions_used:
                    self.analysis.instructions_used.append(instruction)

        return self.analysis

    def _parse_tool_calls(self, lines: list[str]) -> list[ToolCall]:
        """Parse tool call section"""
        tool_calls = []
        i = 0
        while i < len(lines):
            line = lines[i]
            if "- ID:" in line:
                # Extract tool call details
                id_match = re.search(r"'(call_[^']+)'", line)
                tool_id = id_match.group(1) if id_match else ""

                # Next line should have Name
                name = ""
                arguments = ""
                if i + 1 < len(lines):
                    name_line = lines[i + 1]
                    name_match = re.search(r"Name:\s+'([^']+)'", name_line)
                    name = name_match.group(1) if name_match else ""

                # Next line should have Arguments
                if i + 2 < len(lines):
                    args_line = lines[i + 2]
                    args_match = re.search(r"Arguments:\s+'([^']+)'", args_line)
                    arguments = args_match.group(1) if args_match else ""

                if tool_id and name:
                    tool_calls.append(
                        ToolCall(id=tool_id, name=name, arguments=arguments)
                    )

                i += 3
            else:
                i += 1

        return tool_calls

    def _parse_metrics(self, line: str) -> AgentRunMetrics:
        """Parse metrics line"""
        metrics = self.analysis.metrics  # Update existing metrics

        # Extract token counts from current or previous lines
        token_match = re.search(
            r"input=(\d+),\s*output=(\d+),\s*total=(\d+)(?:,\s*reasoning=(\d+))?", line
        )
        if token_match:
            metrics.input_tokens = int(token_match.group(1))
            metrics.output_tokens = int(token_match.group(2))
            metrics.total_tokens = int(token_match.group(3))
            if token_match.group(4):
                metrics.reasoning_tokens = int(token_match.group(4))

        # Extract duration
        duration_match = re.search(r"Duration:\s+([\d.]+)s", line)
        if duration_match:
            metrics.duration = float(duration_match.group(1))

        # Extract tokens per second
        tps_match = re.search(r"([\d.]+)\s+tokens/s", line)
        if tps_match:
            metrics.tokens_per_second = float(tps_match.group(1))

        return metrics

    def _extract_instruction(self, line: str) -> str:
        """Extract instruction text"""
        # Remove DEBUG prefix and clean up
        instruction = line.replace("DEBUG", "").strip()

        # Extract key instructions
        if "markdown" in instruction.lower():
            return "Use proper markdown formatting"
        if "risk disclaimer" in instruction.lower():
            return "Include risk disclaimer"
        if "format" in instruction.lower():
            return "Format responses with headers and structure"

        return ""

    def generate_summary(self) -> str:
        """Generate concise summary report"""
        a = self.analysis

        summary = f"""# Agent Run Analysis
**Timestamp:** {a.timestamp}

## User Request
```
{a.user_prompt}
```

## Tool Execution Summary
- **Total tool calls:** {len(a.tool_calls)}
- **Unique tools used:** {len(set(t.name for t in a.tool_calls))}

### Tool Call Breakdown
"""

        # Group by tool name
        tool_groups: dict[str, list[ToolCall]] = {}
        for tool in a.tool_calls:
            if tool.name not in tool_groups:
                tool_groups[tool.name] = []
            tool_groups[tool.name].append(tool)

        for tool_name, calls in tool_groups.items():
            total_duration = sum(c.duration for c in calls)
            avg_duration = total_duration / len(calls) if calls else 0

            summary += f"\n**{tool_name}** ({len(calls)} calls)\n"
            summary += f"  - Total duration: {total_duration:.2f}s\n"
            summary += f"  - Average duration: {avg_duration:.3f}s\n"

            # Show arguments for first few calls
            if len(calls) <= 5:
                for call in calls:
                    summary += f"    - `{call.arguments}`\n"
            else:
                # Show sample
                summary += f"    - Sample: `{calls[0].arguments}`, `{calls[1].arguments}`, ... ({len(calls)-2} more)\n"

        summary += f"""
## Performance Metrics
- **Input tokens:** {a.metrics.input_tokens:,}
- **Output tokens:** {a.metrics.output_tokens:,}
- **Reasoning tokens:** {a.metrics.reasoning_tokens:,}
- **Total tokens:** {a.metrics.total_tokens:,}
- **Duration:** {a.metrics.duration:.2f}s
- **Throughput:** {a.metrics.tokens_per_second:.2f} tokens/s

## Token Analysis
- **Input ratio:** {(a.metrics.input_tokens / a.metrics.total_tokens * 100) if a.metrics.total_tokens else 0:.1f}%
- **Output ratio:** {(a.metrics.output_tokens / a.metrics.total_tokens * 100) if a.metrics.total_tokens else 0:.1f}%
- **Reasoning ratio:** {(a.metrics.reasoning_tokens / a.metrics.total_tokens * 100) if a.metrics.total_tokens else 0:.1f}%

## Instructions Applied
"""
        if a.instructions_used:
            for instruction in a.instructions_used:
                summary += f"- {instruction}\n"
        else:
            summary += "- (Standard agent instructions)\n"

        # Add timing breakdown
        tool_time = sum(t.duration for t in a.tool_calls)
        model_time = a.metrics.duration - tool_time if a.metrics.duration > tool_time else 0

        summary += f"""
## Timing Breakdown
- **Tool execution time:** {tool_time:.2f}s ({(tool_time / a.metrics.duration * 100) if a.metrics.duration else 0:.1f}%)
- **Model processing time:** {model_time:.2f}s ({(model_time / a.metrics.duration * 100) if a.metrics.duration else 0:.1f}%)

## Optimization Opportunities
"""
        # Analyze for optimization opportunities
        if len(a.tool_calls) > 20:
            summary += f"- **High tool call count:** {len(a.tool_calls)} calls detected. Consider batching or caching.\n"

        slow_tools = [t for t in a.tool_calls if t.duration > 0.5]
        if slow_tools:
            summary += f"- **Slow tool calls:** {len(slow_tools)} calls took >0.5s. Consider optimization or async execution.\n"

        if a.metrics.tokens_per_second < 20:
            summary += f"- **Low throughput:** {a.metrics.tokens_per_second:.1f} tokens/s. Check model configuration.\n"

        if a.metrics.input_tokens > 10000:
            summary += f"- **High input tokens:** {a.metrics.input_tokens:,} tokens. Consider reducing context or using summarization.\n"

        return summary

    def save_analysis(self, output_path: Path | str) -> None:
        """Save analysis to markdown file"""
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        summary = self.generate_summary()
        output_path.write_text(summary)
        print(f"✅ Analysis saved to: {output_path}")


def analyze_agent_run(log_text: str, output_path: Path | str | None = None) -> str:
    """
    Analyze agent run debug log and generate summary

    Args:
        log_text: Raw debug log text
        output_path: Optional path to save analysis report

    Returns:
        Summary text
    """
    analyzer = AgentRunAnalyzer()
    analyzer.parse_log(log_text)
    summary = analyzer.generate_summary()

    if output_path:
        analyzer.save_analysis(output_path)

    return summary


def main():
    """CLI interface for agent run analysis"""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python agent_run_analysis.py <log_file> [output_file]")
        print("\nAnalyzes agent debug logs and generates summary reports")
        sys.exit(1)

    log_file = Path(sys.argv[1])
    if not log_file.exists():
        print(f"❌ Log file not found: {log_file}")
        sys.exit(1)

    output_file = None
    if len(sys.argv) > 2:
        output_file = Path(sys.argv[2])
    else:
        # Auto-generate output filename
        output_file = log_file.parent / f"{log_file.stem}_analysis.md"

    print(f"📊 Analyzing agent run log: {log_file}")
    log_text = log_file.read_text()

    summary = analyze_agent_run(log_text, output_file)
    print("\n" + "=" * 60)
    print(summary)
    print("=" * 60)


if __name__ == "__main__":
    main()
