"""
Unit tests for DevToolsAgent function stubs.
"""

import unittest
from unittest.mock import patch, MagicMock
import subprocess
import builtins

from src.dev_tools.agent import DevToolsAgent
from src.dev_tools.schema import (
    RunFormatterLinterRequest,
    RunUnitTestsRequest,
    CheckGitStatusRequest,
)
from src.dev_tools.function_schemas import get_openai_function_schemas


class FormatterLinterHelpers:
    """Helper methods for mocking formatter and linter subprocesses."""

    def make_mock_black(self, stdout="Black formatted 2 files.", stderr=""):
        """Create a MagicMock for black subprocess output."""
        mock_black = MagicMock()
        mock_black.stdout = stdout
        mock_black.stderr = stderr
        return mock_black

    def make_mock_pylint(self, stdout="Your code has been rated at 9.50/10", stderr=""):
        """Create a MagicMock for pylint subprocess output."""
        mock_pylint = MagicMock()
        mock_pylint.stdout = stdout
        mock_pylint.stderr = stderr
        return mock_pylint


@patch("src.dev_tools.agent.subprocess.run")
class TestFormatterLinter(FormatterLinterHelpers, unittest.TestCase):
    """Unit tests for formatter/linter logic."""

    def setUp(self):
        """Set up a DevToolsAgent instance for testing."""
        self.agent = DevToolsAgent()

    # --- Formatter/Linter Success Cases ---
    def test_run_formatter_linter_success(self, mock_run):
        """Test successful run of formatter/linter."""
        mock_black = self.make_mock_black()
        mock_pylint = self.make_mock_pylint()
        mock_run.side_effect = [mock_black, mock_pylint]
        request = RunFormatterLinterRequest(path="src")
        response = self.agent.run_formatter_linter(request)
        self.assertTrue(response.success)
        self.assertIn("Black formatted", response.black_output)
        self.assertIn("rated at", response.pylint_output)

    def test_run_formatter_linter_custom_path(self, mock_run):
        """Test formatter/linter with a custom file path."""
        mock_black = self.make_mock_black(stdout="Black formatted custom_path.py.")
        mock_pylint = self.make_mock_pylint(
            stdout="Your code has been rated at 10.00/10"
        )
        mock_run.side_effect = [mock_black, mock_pylint]
        request = RunFormatterLinterRequest(path="custom_path.py")
        response = self.agent.run_formatter_linter(request)
        self.assertTrue(response.success)
        self.assertIn("custom_path.py", response.black_output)
        self.assertIn("10.00/10", response.pylint_output)

    def test_run_formatter_linter_output_trimming(self, mock_run):
        """Test that formatter/linter output is trimmed of whitespace."""
        mock_black = self.make_mock_black(
            stdout="  Black formatted 2 files.  ", stderr="  "
        )
        mock_pylint = self.make_mock_pylint(
            stdout="  Your code has been rated at 9.50/10  ", stderr="  "
        )
        mock_run.side_effect = [mock_black, mock_pylint]
        request = RunFormatterLinterRequest(path="src")
        response = self.agent.run_formatter_linter(request)
        self.assertEqual(response.black_output, "Black formatted 2 files.")
        self.assertEqual(response.pylint_output, "Your code has been rated at 9.50/10")

    # --- Formatter/Linter Error and Edge Cases ---
    def test_run_formatter_linter_black_error(self, mock_run):
        """Test error handling when black fails."""
        mock_run.side_effect = [Exception("black not found"), self.make_mock_pylint()]
        request = RunFormatterLinterRequest(path="src")
        response = self.agent.run_formatter_linter(request)
        self.assertFalse(response.success)
        self.assertIn("Error running black", response.black_output)

    def test_run_formatter_linter_pylint_error(self, mock_run):
        """Test error handling when pylint fails."""
        mock_black = self.make_mock_black()
        mock_run.side_effect = [mock_black, Exception("pylint not found")]
        request = RunFormatterLinterRequest(path="src")
        response = self.agent.run_formatter_linter(request)
        self.assertFalse(response.success)
        self.assertIn("Error running pylint", response.pylint_output)

    def test_run_formatter_linter_both_fail(self, mock_run):
        """Test both black and pylint failing."""
        mock_run.side_effect = [
            Exception("black not found"),
            Exception("pylint not found"),
        ]
        request = RunFormatterLinterRequest(path="src")
        response = self.agent.run_formatter_linter(request)
        self.assertFalse(response.success)
        self.assertIn("Error running black", response.black_output)
        self.assertIn("Error running pylint", response.pylint_output)

    @patch("logging.exception")
    def test_run_formatter_linter_logs_errors(self, mock_log, mock_run):
        """Test that errors are logged when formatter/linter fails."""
        mock_run.side_effect = [
            Exception("black not found"),
            Exception("pylint not found"),
        ]
        request = RunFormatterLinterRequest(path="src")
        self.agent.run_formatter_linter(request)
        self.assertEqual(mock_log.call_count, 2)
        mock_log.assert_any_call("Error running black")
        mock_log.assert_any_call("Error running pylint")


@patch("src.dev_tools.agent.subprocess.run")
class TestUnitTests(unittest.TestCase):
    """Unit tests for run_unit_tests logic."""

    def setUp(self):
        """Set up a DevToolsAgent instance for testing."""
        self.agent = DevToolsAgent()

    def test_run_unit_tests_success(self, mock_run):
        """Test successful run of unit tests."""
        mock_proc = MagicMock()
        mock_proc.stdout = (
            "...\n"  # noqa: E501
            "----------------------------------------------------------------------\n"
            "Ran 2 tests in 0.123s\n\nOK\n"
        )
        mock_proc.stderr = ""
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        request = RunUnitTestsRequest(test_path=None)
        response = self.agent.run_unit_tests(request)
        self.assertTrue(response.success)
        self.assertIn("2 tests in", response.summary)
        self.assertEqual([], response.failed_tests)

    def test_run_unit_tests_failure(self, mock_run):
        """Test failed run of unit tests."""
        mock_proc = MagicMock()
        mock_proc.stdout = (
            "FAIL: test_foo (test_module.TestClass)\n"  # noqa: E501
            "----------------------------------------------------------------------\n"
            "Ran 2 tests in 0.123s\n\nFAILED (failures=1)\n"
        )
        mock_proc.stderr = ""
        mock_proc.returncode = 1
        mock_run.return_value = mock_proc
        request = RunUnitTestsRequest(test_path=None)
        response = self.agent.run_unit_tests(request)
        self.assertFalse(response.success)
        self.assertIn("2 tests in", response.summary)
        self.assertIn("FAIL:", " ".join(response.failed_tests))

    def test_run_unit_tests_timeout(self, mock_run):
        """Test timeout when running unit tests."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="unittest", timeout=30)
        request = RunUnitTestsRequest(test_path=None)
        response = self.agent.run_unit_tests(request)
        self.assertFalse(response.success)
        self.assertIn("timed out", response.summary)

    def test_run_unit_tests_exception(self, mock_run):
        """Test exception when running unit tests."""
        mock_run.side_effect = Exception("unittest crashed")
        request = RunUnitTestsRequest(test_path=None)
        response = self.agent.run_unit_tests(request)
        self.assertFalse(response.success)
        self.assertIn("Error running unit tests", response.summary)


@patch("src.dev_tools.agent.subprocess.run")
class TestGitStatus(unittest.TestCase):
    """Unit tests for check_git_status logic."""

    def setUp(self):
        """Set up a DevToolsAgent instance for testing."""
        self.agent = DevToolsAgent()

    def test_git_status_clean(self, mock_run):
        """Test git status with no uncommitted files."""
        mock_proc = MagicMock()
        mock_proc.stdout = ""
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        request = CheckGitStatusRequest()
        response = self.agent.check_git_status(request)
        self.assertFalse(response.has_uncommitted)
        self.assertEqual([], response.uncommitted_files)

    def test_git_status_dirty(self, mock_run):
        """Test git status with uncommitted files."""
        mock_proc = MagicMock()
        mock_proc.stdout = " M src/main.py\n?? new_file.py\n"
        mock_proc.returncode = 0
        mock_run.return_value = mock_proc
        request = CheckGitStatusRequest()
        response = self.agent.check_git_status(request)
        self.assertTrue(response.has_uncommitted)
        self.assertIn("src/main.py", response.uncommitted_files)
        self.assertIn("new_file.py", response.uncommitted_files)

    def test_git_status_timeout(self, mock_run):
        """Test timeout when running git status."""
        mock_run.side_effect = subprocess.TimeoutExpired(cmd="git", timeout=10)
        request = CheckGitStatusRequest()
        response = self.agent.check_git_status(request)
        self.assertFalse(response.has_uncommitted)
        self.assertEqual([], response.uncommitted_files)

    def test_git_status_exception(self, mock_run):
        """Test exception when running git status."""
        mock_run.side_effect = Exception("git crashed")
        request = CheckGitStatusRequest()
        response = self.agent.check_git_status(request)
        self.assertFalse(response.has_uncommitted)
        self.assertEqual([], response.uncommitted_files)


class TestAgentDispatch(FormatterLinterHelpers, unittest.TestCase):
    """Unit tests for agent function dispatch logic."""

    def setUp(self):
        """Set up a DevToolsAgent instance for testing."""
        self.agent = DevToolsAgent()

    @patch("src.dev_tools.agent.subprocess.run")
    def test_call_function_dispatches(self, mock_run):
        """Test that call_function dispatches to the correct agent method."""
        mock_black = self.make_mock_black()
        mock_pylint = self.make_mock_pylint()
        mock_unittest = MagicMock()
        mock_unittest.stdout = (
            "...\n"
            "----------------------------------------------------------------------\n"
            "Ran 2 tests in 0.123s\n\nOK\n"
        )
        mock_unittest.stderr = ""
        mock_unittest.returncode = 0
        mock_git = MagicMock()
        mock_git.stdout = " M src/main.py\n"
        mock_git.returncode = 0
        mock_run.side_effect = [mock_black, mock_pylint, mock_unittest, mock_git]
        resp1 = self.agent.call_function("run_formatter_linter", {"path": None})
        self.assertTrue(resp1.success)
        resp2 = self.agent.call_function("run_unit_tests", {"test_path": None})
        self.assertTrue(resp2.success)
        resp3 = self.agent.call_function("check_git_status", {})
        self.assertTrue(resp3.has_uncommitted)
        with self.assertRaises(ValueError):
            self.agent.call_function("not_a_function", {})


class TestChatLoopIntegration(unittest.TestCase):
    """Integration-style tests for the chat loop (OpenAI mocked)."""

    @patch("openai.chat.completions.create")
    @patch("src.dev_tools.agent.subprocess.run")
    def test_chat_loop_formatter_linter(self, mock_subprocess_run, mock_openai_create):
        """Test chat loop with formatter/linter function call."""
        # Mock OpenAI: first call returns a function_call, second returns assistant message
        function_call_message = MagicMock()
        function_call_message.function_call = MagicMock()
        function_call_message.function_call.name = "run_formatter_linter"
        function_call_message.function_call.arguments = '{"path": "src"}'
        function_call_message.content = None
        function_call_message.role = "assistant"
        function_call_message.model_dump = lambda: {}
        assistant_message = MagicMock()
        assistant_message.function_call = None
        assistant_message.content = "Formatting complete!"
        assistant_message.role = "assistant"
        assistant_message.model_dump = lambda: {}
        mock_openai_create.side_effect = [
            MagicMock(
                choices=[MagicMock(message=function_call_message, finish_reason=None)]
            ),
            MagicMock(
                choices=[MagicMock(message=assistant_message, finish_reason="stop")]
            ),
        ]
        # Mock subprocess for black and pylint
        mock_black = MagicMock(
            stdout="Black formatted 2 files.", stderr="", returncode=0
        )
        mock_pylint = MagicMock(
            stdout="Your code has been rated at 9.50/10", stderr="", returncode=0
        )
        mock_subprocess_run.side_effect = [mock_black, mock_pylint]
        # Patch input to simulate user and exit after one loop
        with patch.object(builtins, "input", side_effect=["Format my code", "exit"]):
            function_schemas = get_openai_function_schemas()
            agent = DevToolsAgent()
            agent.run_openai_chat_loop(function_schemas, model="gpt-4o")
        # Assert OpenAI was called twice (function call, then assistant)
        self.assertEqual(mock_openai_create.call_count, 2)
        # Assert subprocess was called for black and pylint
        self.assertEqual(mock_subprocess_run.call_count, 2)

    @patch("openai.chat.completions.create")
    @patch("src.dev_tools.agent.subprocess.run")
    def test_chat_loop_multiple_function_calls(
        self, mock_subprocess_run, mock_openai_create
    ):
        """Test chat loop with multiple function calls before assistant message."""
        # Simulate two function calls before assistant message
        func_call1 = MagicMock()
        func_call1.function_call = MagicMock()
        func_call1.function_call.name = "run_formatter_linter"
        func_call1.function_call.arguments = '{"path": "src"}'
        func_call1.content = None
        func_call1.role = "assistant"
        func_call1.model_dump = lambda: {}
        func_call2 = MagicMock()
        func_call2.function_call = MagicMock()
        func_call2.function_call.name = "check_git_status"
        func_call2.function_call.arguments = "{}"
        func_call2.content = None
        func_call2.role = "assistant"
        func_call2.model_dump = lambda: {}
        assistant_message = MagicMock()
        assistant_message.function_call = None
        assistant_message.content = "All done!"
        assistant_message.role = "assistant"
        assistant_message.model_dump = lambda: {}
        mock_openai_create.side_effect = [
            MagicMock(choices=[MagicMock(message=func_call1, finish_reason=None)]),
            MagicMock(choices=[MagicMock(message=func_call2, finish_reason=None)]),
            MagicMock(
                choices=[MagicMock(message=assistant_message, finish_reason="stop")]
            ),
        ]
        # Mock subprocess for black, pylint, git
        mock_black = MagicMock(
            stdout="Black formatted 2 files.", stderr="", returncode=0
        )
        mock_pylint = MagicMock(
            stdout="Your code has been rated at 9.50/10", stderr="", returncode=0
        )
        mock_git = MagicMock(stdout=" M src/main.py\n", stderr="", returncode=0)
        mock_subprocess_run.side_effect = [mock_black, mock_pylint, mock_git]
        with patch.object(
            builtins, "input", side_effect=["Format and check git", "exit"]
        ):
            function_schemas = get_openai_function_schemas()
            agent = DevToolsAgent()
            agent.run_openai_chat_loop(function_schemas, model="gpt-4o")
        self.assertEqual(mock_openai_create.call_count, 3)
        self.assertEqual(mock_subprocess_run.call_count, 3)

    @patch("openai.chat.completions.create")
    @patch("src.dev_tools.agent.subprocess.run")
    def test_chat_loop_exit_immediately(self, mock_subprocess_run, mock_openai_create):
        """Test chat loop exits immediately when user types 'exit'."""
        with patch.object(builtins, "input", side_effect=["exit"]):
            function_schemas = get_openai_function_schemas()
            agent = DevToolsAgent()
            agent.run_openai_chat_loop(function_schemas, model="gpt-4o")
        self.assertEqual(mock_openai_create.call_count, 0)
        self.assertEqual(mock_subprocess_run.call_count, 0)

    @patch("openai.chat.completions.create")
    @patch("src.dev_tools.agent.subprocess.run")
    def test_chat_loop_non_function_assistant_message(
        self, mock_subprocess_run, mock_openai_create
    ):
        """Test chat loop returns assistant message without function call."""
        # Model returns an assistant message (no function_call) immediately
        assistant_message = MagicMock()
        assistant_message.function_call = None
        assistant_message.content = "I don't understand."
        assistant_message.role = "assistant"
        assistant_message.model_dump = lambda: {}
        mock_openai_create.side_effect = [
            MagicMock(
                choices=[MagicMock(message=assistant_message, finish_reason="stop")]
            ),
        ]
        with patch.object(
            builtins, "input", side_effect=["What is the meaning of life?", "exit"]
        ):
            function_schemas = get_openai_function_schemas()
            agent = DevToolsAgent()
            agent.run_openai_chat_loop(function_schemas, model="gpt-4o")
        self.assertEqual(mock_openai_create.call_count, 1)
        self.assertEqual(mock_subprocess_run.call_count, 0)


if __name__ == "__main__":
    unittest.main()
