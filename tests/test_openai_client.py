"""
Unit tests for the OpenAI client utility functions in the AI Agents project.
"""

import unittest
from unittest.mock import patch, MagicMock
from src.openai_client import get_openai_completion


class TestOpenAIClient(unittest.TestCase):
    """Test suite for OpenAI client helper functions."""

    @patch("src.openai_client.openai.chat.completions.create")
    def test_get_openai_completion(self, mock_create):
        """Test get_openai_completion returns expected content from mocked API."""
        # Arrange: Mock the OpenAI API response for openai>=1.0.0
        mock_choice = MagicMock()
        mock_choice.message.content = "Hello, world!"
        mock_create.return_value.choices = [mock_choice]
        prompt = "Say hello"

        # Act
        result = get_openai_completion(prompt)

        # Assert
        self.assertEqual("Hello, world!", result)


if __name__ == "__main__":
    unittest.main()
