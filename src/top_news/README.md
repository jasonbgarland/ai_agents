# Top News Agent

A complete AI agent for fetching and summarizing the top news stories of the day using OpenAI's language models and web search tools.

## Overview

The Top News Agent retrieves the top N news stories for the current day and returns a Markdown table with each story's headline and a short summary.

## Features

- **Web Search Integration**: Uses OpenAI's GPT models and web search tools to find current news
- **Structured Output**: Returns a Markdown table for easy reading or further processing
- **Configurable**: Choose how many stories to fetch (1-10)
- **Error Handling**: Provides clear feedback for invalid requests or API errors

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
from src.top_news.agent import top_news

# Fetch the top 5 news stories
table = top_news(5)
print(table)
```

### Example Output

```markdown
| Headline | Summary   |
| -------- | --------- |
| Story 1  | Summary 1 |
| Story 2  | Summary 2 |
| Story 3  | Summary 3 |
| Story 4  | Summary 4 |
| Story 5  | Summary 5 |
```

### Running Examples

Run the example script to see the agent in action:

```bash
python -m src.top_news.example
```

## API Reference

### `top_news(num_stories: int) -> str`

Fetches the top N news stories of the day and returns a Markdown table.

**Parameters:**

- `num_stories` (int): Number of top news stories to fetch (max 10)

**Returns:**

- `str`: Markdown table of headlines and summaries, or an error message

**Error Handling:**

- If you request more than 10 stories, a helpful error message is returned.
- If the API call fails, an error message is returned.

## Configuration

The agent uses the following OpenAI configuration:

- **Model**: `gpt-4.1` (configured in `agent.py`)
- **API Key**: Read from `OPENAI_API_KEY` environment variable
