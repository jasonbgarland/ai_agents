"""
Command-line interface for AI Agents project.

Provides subcommands for interacting with the top news and daily standup agents.
"""

import click
from src.top_news.agent import top_news
from src.daily_standup.agent import daily_standup_with_output as standup


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


if __name__ == "__main__":
    ai()
