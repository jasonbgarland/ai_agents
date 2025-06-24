"""
Unit tests for the Top News Agent.
"""

import unittest
from unittest.mock import patch

from src.top_news.agent import top_news


class TestTopNewsAgent(unittest.TestCase):
    """Test suite for the top_news agent function."""

    def test_top_news_returns_table_with_five_stories(self):
        """Test that top_news returns a Markdown table with five stories."""
        # Mock response from OpenAI client
        mock_response = """| Headline | Summary |
|---|---|
| Story 1 | Summary 1 |
| Story 2 | Summary 2 |
| Story 3 | Summary 3 |
| Story 4 | Summary 4 |
| Story 5 | Summary 5 |"""
        with patch("src.top_news.agent.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.responses.create.return_value.output_text = mock_response
            result = top_news(5)
            self.assertIn("| Headline | Summary |", result)
            # Check that there are 7 rows (header, separator, 5 stories)
            rows = [
                line for line in result.splitlines() if line.strip().startswith("|")
            ]
            self.assertEqual(7, len(rows))  # header + separator + 5 stories
            self.assertIn("Story 5", result)

    def test_top_news_with_zero_stories(self):
        """Test that requesting zero stories returns a no stories message."""
        result = top_news(0)
        self.assertIn("No stories requested", result)

    def test_top_news_with_negative_stories(self):
        """Test that requesting a negative number of stories returns a no stories message."""
        result = top_news(-3)
        self.assertIn("No stories requested", result)

    def test_top_news_with_too_many_stories(self):
        """Test that requesting more than 10 stories returns a too many stories message."""
        result = top_news(15)
        self.assertIn("Too many stories requested", result)

    def test_top_news_with_non_integer(self):
        """Test that passing a non-integer returns an invalid input message."""
        result = top_news("five")
        self.assertIn("must be an integer", result)

    def test_top_news_api_exception(self):
        """Test that an API exception returns an error message."""
        with patch("src.top_news.agent.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.responses.create.side_effect = Exception("API error!")
            result = top_news(3)
            self.assertIn("Error fetching news", result)

    def test_top_news_api_returns_unexpected_format(self):
        """Test that an unexpected API response is returned as-is."""
        mock_response = "No news found today."
        with patch("src.top_news.agent.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.responses.create.return_value.output_text = mock_response
            result = top_news(2)
            self.assertEqual(mock_response, result)

    def test_top_news_with_max_stories(self):
        """Test that requesting the maximum number of stories returns a table with 10 stories."""
        mock_response = """| Headline | Summary |
|---|---|
""" + "\n".join(
            [f"| Story {i} | Summary {i} |" for i in range(1, 11)]
        )
        with patch("src.top_news.agent.OpenAI") as MockOpenAI:
            instance = MockOpenAI.return_value
            instance.responses.create.return_value.output_text = mock_response
            result = top_news(10)
            rows = [
                line for line in result.splitlines() if line.strip().startswith("|")
            ]
            self.assertEqual(12, len(rows))  # header + separator + 10 stories
            self.assertIn("Story 10", result)


if __name__ == "__main__":
    unittest.main()
