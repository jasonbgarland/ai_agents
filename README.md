# AI Agents Learning Project

This project is a collection of AI agents built for learning and experimenting with AI agent development. Each agent is designed to explore different aspects of autonomous systems, from simple task automation to complex reasoning and decision-making.

## Project Structure

- `src/` - Contains the source code for all AI agents
  - `cli.py` - Main CLI implementation (Click commands)
  - `top_news/` - Top news agent code
  - `daily_standup/` - Daily standup agent code
  - `bug_report/` - Bug report agent code
- `ai` - CLI entrypoint script (run as `./ai`)
- `tests/` - Contains test files for agent functionality
- `requirements.txt` - Python dependencies for the project

## AI Agents

| Agent Name    | Summary                                                    | Capabilities                                                                         | README                                |
| ------------- | ---------------------------------------------------------- | ------------------------------------------------------------------------------------ | ------------------------------------- |
| Daily Standup | Automates daily standup meeting preparation and summaries  | Natural Language Processing, Structured Outputs                                      | [README](src/daily_standup/README.md) |
| Top News      | Fetches and summarizes the top news stories of the day     | Web Search (Tool call - built in), Summarization, Markdown Table Output              | [README](src/top_news/README.md)      |
| Bug Report    | Interactive bug reporting agent for structured bug reports | Multi-turn Conversation, Conversation State, Input Validation, Pydantic Model Output | [README](src/bug_report/README.md)    |
| Dev Tools     | OpenAI-powered developer automation agent                  | Natural Language Chat, Custom Function Calling (multiple functions)                  | [README](src/dev_tools/README.md)     |

## Getting Started

1. Create and activate a virtual environment:

   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On macOS/Linux
   ```

2. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Navigate to any agent's directory to explore its functionality and run examples.

## AI Agents CLI

This project includes a command-line interface (CLI) for interacting with AI-powered agents.

### What is it?

The CLI provides access to three agents:

- **news**: Fetches the top news stories of the day and summarizes them in a table.
- **standup**: Processes a daily standup status update and formats it into structured sections (yesterday, today, blockers).
- **bug-report**: Guides you through reporting a software bug interactively, collecting all required details and outputting a structured report.

### How to use

#### 1. Run the CLI from the project root:

```
./ai [COMMAND] [OPTIONS]
```

#### 2. Available commands:

- **news**: Fetch top news stories

  - Usage: `./ai news NUM_STORIES`
  - Example: `./ai news 5`
  - `NUM_STORIES` is the number of top stories to fetch (max 10).

- **standup**: Format a daily standup update

  - Usage: `./ai standup "YOUR STATUS UPDATE"`
  - Example: `./ai standup "Yesterday I fixed bugs. Today I am working on the news agent. No blockers."`
  - Enclose your status update in quotes.

- **bug-report**: Start an interactive bug report session

  - Usage: `./ai bug-report`
  - Example: `./ai bug-report`
  - The agent will prompt you for all required bug details (project, error, steps, severity) and output a structured report.

- **file-search**: Ask a question about one or more text files

  - Usage: `./ai file-search FILE1 [FILE2 ...] "Your question here"`

- **dev-tools**: Start the OpenAI-powered developer tools chat loop
  - Usage: `./ai dev-tools`
  - Example: `./ai dev-tools`
  - This launches an interactive session where you can type requests like:
    - `Format my code`
    - `Run all unit tests`
    - `Check for uncommitted git files`
    - Type `exit` to quit.

#### 3. Help

To see all available commands and options:

```
./ai --help
./ai news --help
./ai standup --help
./ai bug-report --help
./ai file-search --help
./ai dev-tools --help
```

---

**Note:**

- Make sure your dependencies are installed (`pip install -r requirements.txt`).
- The CLI requires a valid OpenAI API key set in your environment as `OPENAI_API_KEY`.

## Future Work

- Support for non-plain-text file types (PDF, DOCX, CSV, etc.) in the File Search Agent
- CLI-level integration tests for all commands using Click's CliRunner
- Further feature enhancements or agent types as needed
