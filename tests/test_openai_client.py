import unittest
from unittest.mock import patch, MagicMock
from src.openai_client import get_openai_completion, soothing_sunset_description

class TestOpenAIClient(unittest.TestCase):
    @patch('src.openai_client.openai.chat.completions.create')
    def test_get_openai_completion(self, mock_create):
        # Arrange: Mock the OpenAI API response for openai>=1.0.0
        mock_choice = MagicMock()
        mock_choice.message.content = 'Hello, world!'
        mock_create.return_value.choices = [mock_choice]
        prompt = "Say hello"

        # Act
        result = get_openai_completion(prompt)

        # Assert
        self.assertEqual(result, 'Hello, world!')

    def test_soothing_sunset_description_real_api(self):
        """
        This test calls the real OpenAI API for a soothing sunset description and checks that the response is non-empty and contains at least one of: sun, sunset, horizon, or sky.
        """
        response = soothing_sunset_description()
        print(f"OpenAI response: {response}")
        self.assertTrue(isinstance(response, str) and len(response) > 0, "Response should be a non-empty string.")
        keywords = ["sun", "sunset", "horizon", "sky"]
        self.assertTrue(any(word in response.lower() for word in keywords),
                        f"Response should mention at least one of: {', '.join(keywords)}.")

if __name__ == '__main__':
    unittest.main()
