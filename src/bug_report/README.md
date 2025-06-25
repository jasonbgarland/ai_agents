# Bug Report Agent

A conversational agent for collecting structured bug reports using OpenAI's conversation state feature. The agent guides users through providing all necessary details for a bug report, validates input, and outputs a structured report.

## Features

- Multi-turn, natural language input
- Extracts: project affected, error message, steps to reproduce, severity
- Defaults severity to 'Medium' if not specified
- Prompts for missing or invalid fields
- Handles errors gracefully

## Usage

### Interactive Example

Run the example script from the project root:

```sh
source .venv/bin/activate
python -m src.bug_report.example
```

### CLI Command

You can also start an interactive bug report session via the CLI:

```sh
source .venv/bin/activate
python -m src.cli bug-report
```

### Integration

Import and use the agent in your own code:

```python
from src.bug_report.agent import BugReportAgent

agent = BugReportAgent()
agent.report_bug()  # Interactive CLI
```

Or use `process_turn` for programmatic multi-turn flows.

## Schema

The bug report is structured as:

- `project_affected` (str)
- `error_message` (str)
- `steps_to_reproduce` (List[str])
- `severity` (Low | Medium | High)

## Extending

- Add new fields to the schema and update prompts as needed
- Integrate with your CLI or other agents
- See code comments and tests for guidance

---
