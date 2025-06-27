"""
Command-line interface for AI Agents project.

Provides subcommands for interacting with the top news and daily standup agents.
"""

import click
from src.top_news.agent import top_news
from src.daily_standup.agent import daily_standup_with_output as standup
from src.bug_report.agent import BugReportAgent
from src.file_search.agent import FileSearchAgent
from src.dev_tools.agent import DevToolsAgent
from src.dev_tools.function_schemas import get_openai_function_schemas


@click.group()
def ai():
    """AI Agents CLI: Use subcommands for each agent."""
    # No setup required for the CLI group
    pass  # pylint: disable=unnecessary-pass


@ai.command(name="news")
@click.argument("num_stories", type=int)
def news_cmd(num_stories):
    """Fetch the top news stories of the day and list summaries."""
    result = top_news(num_stories)
    click.echo(result)


@ai.command(name="standup")
@click.argument("status_input", type=str)
def standup_cmd(status_input):
    """Gather daily status and present it in a standard format. (Enclose your status in quotes)"""
    result = standup(status_input)
    click.echo(result)


@ai.command(name="bug-report")
def bug_report_cmd():
    """Start an interactive bug report session."""
    agent = BugReportAgent()
    agent.report_bug()


@ai.command(name="file-search")
@click.argument("file_paths", type=click.Path(exists=True), nargs=-1)
@click.argument("question", type=str)
def file_search_cmd(file_paths, question):
    """
    Ask a natural language question about the contents of one or more plain text files using the File Search Agent.

    Only plain text files are supported. Other formats will result in an error.

    Usage:
      python src/cli.py file-search FILE1 [FILE2 ...] "Your question here"

    Example:
      python src/cli.py file-search notes.txt report.txt "Summarize the main points."
    """
    agent = FileSearchAgent()
    file_ids = []
    for path in file_paths:
        try:
            file_id = agent.upload_file_from_path(path)
            click.echo(f"Uploaded file '{path}' with ID: {file_id}")
            file_ids.append(file_id)
        except ValueError as e:
            click.echo(str(e))
    if file_ids:
        final_answer = agent.answer_question_multiple_files(file_ids, question)
        click.echo(f"\nSYNTHESIZED ANSWER:\n{final_answer}")


@ai.command(name="dev-tools")
def dev_tools_cmd():
    """Start an interactive DevToolsAgent session (OpenAI-powered developer tools)."""
    agent = DevToolsAgent()
    function_schemas = get_openai_function_schemas()
    agent.run_openai_chat_loop(function_schemas)


if __name__ == "__main__":
    ai()
