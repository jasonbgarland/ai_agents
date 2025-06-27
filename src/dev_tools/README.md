# DevToolsAgent

A developer automation agent that uses OpenAI function calling to run code formatting, linting, unit tests, and git status checks based on natural language prompts. Built for extensibility, robust error handling, and easy integration with CLI or other interfaces.

## Features

- **OpenAI Function Calling**: Natural language interface for running developer tools.
- **Formatter/Linter**: Runs `black` and `pylint` with output and error handling.
- **Unit Test Runner**: Runs Python `unittest` discovery, parses results, and reports failures.
- **Git Status**: Checks for uncommitted files using `git status --porcelain`.
- **Pydantic Schemas**: All function arguments and results are validated and structured.
- **Extensible**: Add new developer tool integrations easily.
- **Tested**: Comprehensive unit tests for all subprocess logic and error cases.

## Usage

### As a Library

```python
from src.dev_tools.agent import DevToolsAgent
from src.dev_tools.schema import RunFormatterLinterRequest

agent = DevToolsAgent()
request = RunFormatterLinterRequest(path="src")
response = agent.run_formatter_linter(request)
print(response.success, response.black_output, response.pylint_output)
```

### OpenAI Chat Loop Demo

Run the interactive chat loop (requires OpenAI API key in `.env`):

```bash
python -m src.dev_tools.example
```

### CLI Integration

You can integrate the agent into a Click CLI or other interface. See `src/bug_report/example.py` for a reference CLI pattern.

## File Structure

- `agent.py` — Main agent logic, subprocess calls, OpenAI chat loop
- `schema.py` — Pydantic schemas for all agent functions
- `function_schemas.py` — OpenAI-compatible function schemas
- `example.py` — Minimal demo entry point
- `tests/` — Unit tests for all agent functions

## Extending

To add a new developer tool:

1. Define request/response schemas in `schema.py`.
2. Add a method to `DevToolsAgent` for the new tool.
3. Register the function in `call_function` and `function_schemas.py`.
4. Add unit tests for the new logic.

## Requirements

- Python 3.8+
- OpenAI Python SDK
- Pydantic
- black, pylint, git (for subprocess calls)

## Security

- User input is validated via Pydantic.
- No secrets or API keys are committed to the repo.

## License

MIT
