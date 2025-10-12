# Agent Run Analysis Tool - Usage Guide

## Overview
The `agent_run_analysis.py` tool parses DEBUG logs from agent runs and generates concise, actionable summaries.

## Features

✅ **Tool Call Analysis**
- Counts and groups tool calls by type
- Calculates average execution time per tool
- Identifies slow or problematic calls

✅ **Performance Metrics**
- Token usage breakdown (input/output/reasoning)
- Throughput analysis (tokens per second)
- Timing breakdown (tool vs model processing)

✅ **Optimization Recommendations**
- Identifies high tool call counts
- Detects slow tool executions
- Suggests caching and batching opportunities

✅ **Instruction Tracking**
- Extracts applied instructions from logs
- Highlights formatting and compliance requirements

## Usage

### Method 1: Command Line

```bash
# Analyze a log file
python src/utils/agent_run_analysis.py debug.log

# Specify output file
python src/utils/agent_run_analysis.py debug.log analysis_report.md
```

### Method 2: Python API

```python
from pathlib import Path
from src.utils.agent_run_analysis import analyze_agent_run

# Read log file
log_text = Path("debug.log").read_text()

# Generate analysis
summary = analyze_agent_run(log_text, output_path="reports/analysis.md")

# Print summary
print(summary)
```

### Method 3: In-Code Analysis

```python
from src.utils.agent_run_analysis import AgentRunAnalyzer

analyzer = AgentRunAnalyzer()

# Parse log
analysis = analyzer.parse_log(log_text)

# Access structured data
print(f"Tool calls: {len(analysis.tool_calls)}")
print(f"Total tokens: {analysis.metrics.total_tokens}")
print(f"Duration: {analysis.metrics.duration}s")

# Generate summary
summary = analyzer.generate_summary()
```

## Output Format

The tool generates a comprehensive markdown report with:

### 1. User Request
Shows the original prompt that triggered the agent run

### 2. Tool Execution Summary
- Total tool calls
- Unique tools used
- Breakdown by tool type with timing

Example:
```markdown
**get_current_stock_price** (27 calls)
  - Total duration: 5.12s
  - Average duration: 0.190s
  - Sample: symbol: ^GSPC, symbol: ^DJI, ... (25 more)
```

### 3. Performance Metrics
Complete token and timing analysis:
- Input/output/reasoning tokens
- Duration and throughput
- Token ratio breakdown

### 4. Timing Breakdown
Shows where time was spent:
- Tool execution time (%)
- Model processing time (%)

### 5. Optimization Opportunities
Actionable recommendations:
- High tool call count warnings
- Slow tool call detection
- Throughput optimization suggestions
- Context size recommendations

## Example Analysis

Input: Agent run with 27 stock price lookups

Output summary:
```markdown
## Tool Execution Summary
- Total tool calls: 27
- Unique tools used: 1

**get_current_stock_price** (27 calls)
  - Total duration: 5.12s
  - Average duration: 0.190s

## Performance Metrics
- Total tokens: 2,555
- Duration: 30.91s
- Throughput: 30.32 tokens/s

## Timing Breakdown
- Tool execution time: 5.12s (16.6%)
- Model processing time: 25.79s (83.4%)

## Optimization Opportunities
- High tool call count: 27 calls detected. Consider batching or caching.
```

## Integration with Agent Workflow

### Automatic Analysis After Run

```python
from src.utils.agent_run_analysis import analyze_agent_run

# Run agent with debug mode
agent.debug_mode = True
response = agent.run(prompt)

# Capture debug output and analyze
# (Requires capturing DEBUG logs to file or string)
log_text = capture_debug_logs()
summary = analyze_agent_run(log_text, "reports/last_run_analysis.md")
```

### CI/CD Integration

```bash
# In your CI pipeline
python src/utils/agent_run_analysis.py logs/agent_run.log reports/performance_analysis.md

# Check for performance regressions
if grep -q "Low throughput" reports/performance_analysis.md; then
    echo "⚠️ Performance regression detected"
    exit 1
fi
```

## Benefits

1. **Performance Monitoring**: Track token usage and execution time trends
2. **Optimization**: Identify bottlenecks and optimization opportunities
3. **Cost Analysis**: Understand token consumption patterns
4. **Debugging**: Quickly identify which tools were called and why
5. **Documentation**: Generate reports for stakeholders

## Advanced Features

### Custom Filtering

```python
analyzer = AgentRunAnalyzer()
analysis = analyzer.parse_log(log_text)

# Filter slow tools only
slow_tools = [t for t in analysis.tool_calls if t.duration > 0.5]
print(f"Slow tools: {len(slow_tools)}")

# Calculate tool-specific metrics
tool_times = {}
for tool in analysis.tool_calls:
    if tool.name not in tool_times:
        tool_times[tool.name] = []
    tool_times[tool.name].append(tool.duration)

for tool_name, times in tool_times.items():
    avg_time = sum(times) / len(times)
    print(f"{tool_name}: {avg_time:.3f}s average")
```

### Batch Analysis

```python
from pathlib import Path

# Analyze all logs in directory
log_dir = Path("logs")
for log_file in log_dir.glob("*.log"):
    output = log_file.parent / "reports" / f"{log_file.stem}_analysis.md"
    analyze_agent_run(log_file.read_text(), output)
```

---

**Created**: 2025-10-12
**Location**: `src/utils/agent_run_analysis.py`
