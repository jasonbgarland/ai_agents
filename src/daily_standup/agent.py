"""Daily Standup Agent for processing and formatting team status updates."""

import os
from typing import List

import openai
from dotenv import load_dotenv
from pydantic import BaseModel

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY


class DailyStatus(BaseModel):
    """Pydantic model for structured daily status updates."""

    yesterday: List[str] = []
    today: List[str] = []
    blockers: List[str] = []


def daily_standup(status: str) -> DailyStatus:
    """
    Process daily status in natural language and format it as a structured update.

    Takes a natural language status update and uses OpenAI to parse it into
    structured sections for yesterday, today, and blockers. Returns a formatted
    bulleted list with section headers.

    Args:
        status (str): Natural language status update

    Returns:
        DailyStatus: Parsed status with yesterday, today, and blockers sections

    Raises:
        ValueError: If required information (yesterday or today) is missing

    Example:
        >>> result = daily_standup("Yesterday I worked on the login feature. Today I will attend meetings")
        >>> print(result.yesterday)
        ['worked on the login feature']
    """
    response = openai.responses.parse(
        model="gpt-4.1-nano",
        input=[
            {
                "role": "system",
                "content": (
                    "You are a scrum master for a software development team. "
                    "You are collecting daily standup updates. You want to take the information and "
                    "categorize it into three sections: yesterday, today, and blockers. "
                    "If there is no information for a section, leave it empty. "
                    "Each item in the lists should start with a capital letter."
                ),
            },
            {
                "role": "user",
                "content": status,
            },
        ],
        text_format=DailyStatus,
    )

    parsed_status = response.output_parsed
    missing_info = []

    if parsed_status.yesterday == []:
        missing_info.append("yesterday")
    if parsed_status.today == []:
        missing_info.append("today")
    if parsed_status.blockers == []:
        parsed_status.blockers = ["No blockers"]

    # Check output. Yesterday and today are required so respond appropriately if they are missing.
    if missing_info:
        raise ValueError(
            (
                f"Missing information for: {', '.join(missing_info)}. "
                "Please provide a complete status update. Status for yesterday and today are required."
            )
        )

    return parsed_status


def format_daily_status(parsed_status: DailyStatus) -> str:
    """
    Format a DailyStatus object into a readable bulleted list.

    Args:
        parsed_status (DailyStatus): The parsed status object

    Returns:
        str: Formatted status as a bulleted list with section headers
    """
    formatted_status = (
        "### Daily Standup Update\n"
        "- **Yesterday:**\n"
        + "\n".join([f"  - {item}" for item in parsed_status.yesterday])
        + "\n"
        "- **Today:**\n"
        + "\n".join([f"  - {item}" for item in parsed_status.today])
        + "\n"
        "- **Blockers:**\n"
        + "\n".join([f"  - {item}" for item in parsed_status.blockers])
    )
    return formatted_status


def daily_standup_with_output(status: str) -> str:
    """
    Process daily status and return formatted output or error message.

    Convenience function that processes the status and returns the formatted output or error message.

    Args:
        status (str): Natural language status update

    Returns:
        str: Formatted status or error message
    """
    try:
        parsed_status = daily_standup(status)
        formatted_output = format_daily_status(parsed_status)
        return formatted_output
    except ValueError as e:
        return str(e)


if __name__ == "__main__":
    # Example usage
    EXAMPLE_STATUS = (
        "Yesterday was Sunday. I mostly relaxed but also researched some openAPI info. "
        "Today I am back at work, catching up on emails, and working on the openai agent. "
        "I am not blocked"
    )
    daily_standup_with_output(EXAMPLE_STATUS)
