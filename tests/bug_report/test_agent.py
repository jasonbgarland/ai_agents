"""Unit tests for the BugReportAgent and bug report conversation logic."""

import unittest
from unittest.mock import patch, MagicMock

from src.bug_report.agent import BugReportAgent
from src.bug_report.schema import Severity, BugReport


class TestBugReportAgent(unittest.TestCase):
    """Test cases for the BugReportAgent multi-turn bug reporting logic."""

    @patch("openai.responses.parse")
    def test_process_turn_all_fields(self, mock_parse):
        """Agent completes when all fields are provided in one turn."""
        mock_bug_report = BugReport(
            project_affected="test_project",
            error_message="Something broke",
            steps_to_reproduce=["Step 1", "Step 2"],
            severity=Severity.HIGH,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        state, prompt, is_complete = agent.process_turn("Full bug report input")
        self.assertTrue(is_complete)
        self.assertIn("Thank you! All required information has been collected", prompt)
        self.assertEqual(state.severity, Severity.HIGH)

    @patch("openai.responses.parse")
    def test_process_turn_missing_severity_defaults_medium(self, mock_parse):
        """Agent defaults severity to Medium if missing and all else is present."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=["step1"],
            severity=None,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        state, prompt, is_complete = agent.process_turn("No severity")
        self.assertTrue(is_complete)
        self.assertEqual(state.severity, Severity.MEDIUM)
        self.assertIn("Medium", prompt)
        self.assertIn("no severity was specified", prompt.lower())

    @patch("openai.responses.parse")
    def test_process_turn_missing_steps(self, mock_parse):
        """Agent prompts for steps if missing."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=[],
            severity=Severity.LOW,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("No steps")
        self.assertFalse(is_complete)
        self.assertIn("steps_to_reproduce", prompt)

    @patch("openai.responses.parse")
    def test_process_turn_missing_project(self, mock_parse):
        """Agent prompts for project if missing."""
        mock_bug_report = BugReport(
            project_affected=None,
            error_message="err",
            steps_to_reproduce=["step1"],
            severity=Severity.LOW,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("No project")
        self.assertFalse(is_complete)
        self.assertIn("project_affected", prompt)

    @patch("openai.responses.parse")
    def test_process_turn_missing_error_message(self, mock_parse):
        """Agent prompts for error message if missing."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message=None,
            steps_to_reproduce=["step1"],
            severity=Severity.LOW,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("No error message")
        self.assertFalse(is_complete)
        self.assertIn("error_message", prompt)

    @patch("openai.responses.parse")
    def test_process_turn_multi_turn_completion(self, mock_parse):
        """Agent supports multi-turn completion."""
        mock_bug_report1 = BugReport(
            project_affected="proj",
            error_message=None,
            steps_to_reproduce=[],
            severity=None,
        )
        mock_bug_report2 = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=["step1"],
            severity=Severity.HIGH,
        )
        mock_parse.side_effect = [
            MagicMock(output_parsed=mock_bug_report1),
            MagicMock(output_parsed=mock_bug_report2),
        ]

        agent = BugReportAgent()
        _, _, is_complete = agent.process_turn("Only project")
        state, _, is_complete = agent.process_turn("err, step1, high")
        self.assertTrue(is_complete)
        self.assertEqual(state.severity, Severity.HIGH)

    @patch("openai.responses.parse")
    def test_process_turn_invalid_severity(self, mock_parse):
        """Agent prompts for valid severity if invalid provided."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=["step1"],
            severity="Critical",
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("Invalid severity")
        self.assertFalse(is_complete)
        self.assertIn("severity", prompt.lower())

    @patch("openai.responses.parse")
    def test_process_turn_steps_semicolon_split(self, mock_parse):
        """Agent handles steps as semicolon-separated string."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=["step1; step2; step3"],
            severity=Severity.LOW,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        state, _, _ = agent.process_turn("Steps as semicolon string")
        self.assertIn("steps_to_reproduce", state.model_fields)

    @patch("openai.responses.parse")
    def test_process_turn_severity_explicit_low_high(self, mock_parse):
        """Agent accepts explicit Low/High severity values."""
        for sev in [Severity.LOW, Severity.HIGH]:
            mock_bug_report = BugReport(
                project_affected="proj",
                error_message="err",
                steps_to_reproduce=["step1"],
                severity=sev,
            )
            mock_parse.return_value.output_parsed = mock_bug_report

            agent = BugReportAgent()
            state, _, is_complete = agent.process_turn(f"Severity {sev}")
            self.assertTrue(is_complete)
            self.assertEqual(state.severity, sev)

    @patch("openai.responses.parse")
    def test_process_turn_empty_input(self, mock_parse):
        """Agent prompts for all fields if input is empty."""
        mock_bug_report = BugReport(
            project_affected=None,
            error_message=None,
            steps_to_reproduce=[],
            severity=None,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("")
        self.assertFalse(is_complete)
        self.assertIn("project_affected", prompt)
        self.assertIn("error_message", prompt)
        self.assertIn("steps_to_reproduce", prompt)
        self.assertIn("severity", prompt)

    @patch("openai.responses.parse")
    def test_process_turn_api_validation_error(self, mock_parse):
        """Agent handles API validation errors gracefully."""
        mock_parse.side_effect = Exception("API validation error")
        agent = BugReportAgent()
        _, prompt, is_complete = agent.process_turn("bad input")
        self.assertFalse(is_complete)
        self.assertIn("problem parsing", prompt.lower())

    @patch("openai.responses.parse")
    def test_process_turn_extra_irrelevant_info(self, mock_parse):
        """Agent ignores extra irrelevant info and completes if all fields are present."""
        mock_bug_report = BugReport(
            project_affected="proj",
            error_message="err",
            steps_to_reproduce=["step1"],
            severity=Severity.LOW,
        )
        mock_parse.return_value.output_parsed = mock_bug_report

        agent = BugReportAgent()
        state, _, is_complete = agent.process_turn(
            "This is a bug with extra info: ignore this."
        )
        self.assertTrue(is_complete)
        self.assertEqual(state.project_affected, "proj")
        self.assertEqual(state.severity, Severity.LOW)


if __name__ == "__main__":
    unittest.main()
