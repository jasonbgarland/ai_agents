# Daily Standup Agent

A complete AI agent for processing and formatting daily standup updates using OpenAI's language models.

## Overview

The Daily Standup Agent takes natural language status updates and automatically parses them into structured sections for:

- **Yesterday**: What was accomplished the previous day
- **Today**: What will be worked on today
- **Blockers**: Any obstacles or dependencies

## Features

- **Natural Language Processing**: Uses OpenAI's GPT models to intelligently parse unstructured status updates
- **Structured Output**: Returns organized data with Pydantic models for type safety
- **Validation**: Ensures required information (yesterday and today) is present
- **Formatted Display**: Generates clean, bulleted list output for reports
- **Error Handling**: Provides clear feedback for incomplete status updates

## Installation

Make sure you have the required dependencies installed:

```bash
pip install -r requirements.txt
```

You'll also need an OpenAI API key set in your environment:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

## Usage

### Basic Usage

```python
from src.daily_standup import daily_standup, format_daily_status

# Process a status update
status = "Yesterday I worked on the login feature. Today I will continue with the login feature and start on the signup feature. No blockers."
result = daily_standup(status)

# Format for display
formatted = format_daily_status(result)
print(formatted)
```

### Example Output

```markdown
### Daily Standup Update

- **Yesterday:**
  - worked on the login feature
- **Today:**
  - continue with the login feature
  - start on the signup feature
- **Blockers:**
  - No blockers
```

### Quick Function

For convenience, use `daily_standup_with_output()` to process and print in one call:

```python
from src.daily_standup import daily_standup_with_output

daily_standup_with_output("Yesterday I researched APIs. Today I'm implementing authentication. Blocked by waiting for API keys.")
```

### Running Examples

Run the example script to see the agent in action:

```bash
python src/daily_standup/example.py
```

## API Reference

### `daily_standup(status: str) -> DailyStatus`

Main function that processes a natural language status update.

**Parameters:**

- `status` (str): Natural language status update

**Returns:**

- `DailyStatus`: Parsed status with yesterday, today, and blockers

**Raises:**

- `ValueError`: If required information is missing

### `DailyStatus`

Pydantic model representing a structured status update.

**Fields:**

- `yesterday` (List[str]): List of yesterday's activities
- `today` (List[str]): List of today's planned activities
- `blockers` (List[str]): List of blockers (defaults to ["No blockers"] if empty)

### `format_daily_status(parsed_status: DailyStatus) -> str`

Formats a DailyStatus object into a readable bulleted list.

**Parameters:**

- `parsed_status` (DailyStatus): The parsed status object

**Returns:**

- `str`: Formatted status as markdown with section headers

### `daily_standup_with_output(status: str) -> str`

Convenience function that processes status and returns formatted output or error message.

## Testing

Run the test suite:

```bash
python -m pytest tests/daily_standup/ -v
```

The tests cover:

- Pydantic model validation
- OpenAI API integration (mocked)
- Error handling for missing information
- Output formatting
- End-to-end workflow

## Error Handling

The agent validates that both yesterday and today information are provided:

```python
# This will raise ValueError
daily_standup("I worked on stuff.")  # Missing today information

# This will work
daily_standup("Yesterday I worked on stuff. Today I will work on more stuff.")
```

## Configuration

The agent uses the following OpenAI configuration:

- **Model**: `gpt-4.1-nano` (configured in `agent.py`)
- **API Key**: Read from `OPENAI_API_KEY` environment variable
