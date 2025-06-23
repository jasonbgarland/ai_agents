"""Unit tests for the Daily Standup Agent."""

import unittest
from unittest.mock import Mock, patch
from src.daily_standup.agent import (
    daily_standup, 
    DailyStatus, 
    format_daily_status, 
    daily_standup_with_output
)


class TestDailyStatus(unittest.TestCase):
    """Tests for the DailyStatus Pydantic model."""
    
    def test_daily_status_creation_empty(self):
        """Test creating an empty DailyStatus object."""
        status = DailyStatus()
        self.assertEqual(status.yesterday, [])
        self.assertEqual(status.today, [])
        self.assertEqual(status.blockers, [])

    def test_daily_status_creation_with_data(self):
        """Test creating a DailyStatus object with data."""
        status = DailyStatus(
            yesterday=["worked on login"],
            today=["work on signup", "fix bugs"],
            blockers=["need API key"]
        )
        self.assertEqual(status.yesterday, ["worked on login"])
        self.assertEqual(status.today, ["work on signup", "fix bugs"])
        self.assertEqual(status.blockers, ["need API key"])


class TestFormatDailyStatus(unittest.TestCase):
    """Tests for the format_daily_status function."""
    
    def test_format_complete_status(self):
        """Test formatting a complete status with all sections."""
        status = DailyStatus(
            yesterday=["worked on login feature"],
            today=["continue with login", "start signup feature"],
            blockers=["No blockers"]
        )
        
        result = format_daily_status(status)
        expected = (
            "### Daily Standup Update\n"
            "- **Yesterday:**\n"
            "  - worked on login feature\n"
            "- **Today:**\n"
            "  - continue with login\n"
            "  - start signup feature\n"
            "- **Blockers:**\n"
            "  - No blockers"
        )
        self.assertEqual(result, expected)
    
    def test_format_status_with_multiple_blockers(self):
        """Test formatting a status with multiple blockers."""
        status = DailyStatus(
            yesterday=["research"],
            today=["implement"],
            blockers=["need API access", "waiting for design"]
        )
        
        result = format_daily_status(status)
        self.assertIn("  - need API access", result)
        self.assertIn("  - waiting for design", result)


class TestDailyStandup(unittest.TestCase):
    """Tests for the daily_standup function."""
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_success(self, mock_parse):
        """Test successful parsing of daily status."""
        # Mock the OpenAI response
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=["worked on features"],
            today=["continue development"],
            blockers=["No blockers"]
        )
        mock_parse.return_value = mock_response
        
        result = daily_standup("Yesterday I worked on features. Today I continue development.")
        
        self.assertIsInstance(result, DailyStatus)
        self.assertEqual(result.yesterday, ["worked on features"])
        self.assertEqual(result.today, ["continue development"])
        self.assertEqual(result.blockers, ["No blockers"])
        
        # Verify OpenAI was called with correct parameters
        mock_parse.assert_called_once()
        call_args = mock_parse.call_args
        self.assertEqual(call_args[1]['model'], "gpt-4.1-nano")
        self.assertEqual(call_args[1]['text_format'], DailyStatus)
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_missing_yesterday(self, mock_parse):
        """Test handling of missing yesterday information."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=[],  # Empty yesterday
            today=["work on new feature"],
            blockers=["No blockers"]
        )
        mock_parse.return_value = mock_response
        
        with self.assertRaises(ValueError) as cm:
            daily_standup("Today I will work on new feature.")
        
        self.assertIn("Missing information for: yesterday", str(cm.exception))
        self.assertIn("Status for yesterday and today are required", str(cm.exception))
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_missing_today(self, mock_parse):
        """Test handling of missing today information."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=["worked on feature"],
            today=[],  # Empty today
            blockers=["No blockers"]
        )
        mock_parse.return_value = mock_response
        
        with self.assertRaises(ValueError) as cm:
            daily_standup("Yesterday I worked on feature.")
        
        self.assertIn("Missing information for: today", str(cm.exception))
        self.assertIn("Status for yesterday and today are required", str(cm.exception))
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_missing_both_yesterday_and_today(self, mock_parse):
        """Test handling of missing both yesterday and today information."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=[],  # Empty yesterday
            today=[],      # Empty today
            blockers=["No blockers"]
        )
        mock_parse.return_value = mock_response
        
        with self.assertRaises(ValueError) as cm:
            daily_standup("I have no specific updates.")
        
        self.assertIn("Missing information for: yesterday, today", str(cm.exception))
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_empty_blockers_defaults_to_no_blockers(self, mock_parse):
        """Test that empty blockers defaults to 'No blockers'."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=["worked on features"],
            today=["continue development"],
            blockers=[]  # Empty blockers
        )
        mock_parse.return_value = mock_response
        
        result = daily_standup("Yesterday I worked on features. Today I continue development.")
        
        self.assertEqual(result.blockers, ["No blockers"])
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    def test_daily_standup_preserves_existing_blockers(self, mock_parse):
        """Test that existing blockers are preserved."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=["worked on features"],
            today=["continue development"],
            blockers=["need API access", "waiting for review"]
        )
        mock_parse.return_value = mock_response
        
        result = daily_standup("Yesterday I worked on features. Today I continue development. Blocked by API access and review.")
        
        self.assertEqual(result.blockers, ["need API access", "waiting for review"])


class TestDailyStandupWithOutput(unittest.TestCase):
    """Tests for the daily_standup_with_output function."""
    
    @patch('src.daily_standup.agent.openai.responses.parse')
    @patch('builtins.print')
    def test_daily_standup_with_output_prints_formatted_status(self, mock_print, mock_parse):
        """Test that daily_standup_with_output prints the formatted status."""
        mock_response = Mock()
        mock_response.output_parsed = DailyStatus(
            yesterday=["worked on login"],
            today=["work on signup"],
            blockers=["No blockers"]
        )
        mock_parse.return_value = mock_response
        
        result = daily_standup_with_output("Yesterday I worked on login. Today I work on signup.")
        
        # Verify print was called
        mock_print.assert_called_once()
        printed_content = mock_print.call_args[0][0]
        self.assertIn("### Daily Standup Update", printed_content)
        self.assertIn("worked on login", printed_content)
        self.assertIn("work on signup", printed_content)
        
        # Verify return value
        self.assertIsInstance(result, DailyStatus)
        self.assertEqual(result.yesterday, ["worked on login"])


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete workflow."""
    
    def test_end_to_end_workflow(self):
        """Test the complete workflow from input to formatted output."""
        # This test would require a real OpenAI API call, so we'll mock it
        with patch('src.daily_standup.agent.openai.responses.parse') as mock_parse:
            mock_response = Mock()
            mock_response.output_parsed = DailyStatus(
                yesterday=["researched openAPI info", "relaxed"],
                today=["catch up on emails", "work on openai agent"],
                blockers=["No blockers"]
            )
            mock_parse.return_value = mock_response
            
            status_text = "Yesterday was Sunday. I mostly relaxed but also researched some openAPI info. Today I am back at work, catching up on emails, and working on the openai agent. I am not blocked"
            
            # Test the main function
            result = daily_standup(status_text)
            
            # Test formatting
            formatted = format_daily_status(result)
            
            self.assertIn("researched openAPI info", formatted)
            self.assertIn("catch up on emails", formatted)
            self.assertIn("No blockers", formatted)
            self.assertIn("### Daily Standup Update", formatted)


if __name__ == "__main__":
    unittest.main()
