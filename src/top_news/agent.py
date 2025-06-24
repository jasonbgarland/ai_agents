"""
Agent module for fetching and summarizing the top news stories of the day.
"""

from openai import OpenAI


def top_news(num_stories: int) -> str:
    """
    Fetch the top N news stories of the day and return a Markdown table with headline and summary.

    Args:
        num_stories (int): Number of top news stories to fetch (max 10).

    Returns:
        str: Markdown table of headlines and summaries, or a message if no stories requested.
    """
    if not isinstance(num_stories, int):
        return "Invalid input: num_stories must be an integer."
    if num_stories <= 0:
        return "No stories requested. Please specify a positive number of stories."
    if num_stories > 10:
        return "Too many stories requested. Please request 10 or fewer."
    try:
        client = OpenAI()
        prompt = (
            f"Find the top {num_stories} news stories from today. "
            "Return a Markdown table with two columns: 'Headline' and 'Summary'. "
            "Each row should be a different story."
        )
        response = client.responses.create(
            model="gpt-4.1", tools=[{"type": "web_search_preview"}], input=prompt
        )
        return response.output_text
    except Exception as exc:  # pylint: disable=broad-except
        # Log the error in a real system
        return f"Error fetching news: {exc}"
