"""
Agent for handling developer tool function calls (formatter/linter, tests, git status).

Responsibilities:
- Expose functions for OpenAI function calling
- Validate and parse requests/responses using Pydantic schemas
- (For now) Return mock responses for each function
"""

import json
import logging
import os
import re
import subprocess
from typing import Any, Dict

from dotenv import load_dotenv
import openai

from src.dev_tools.schema import (
    RunFormatterLinterRequest,
    RunFormatterLinterResponse,
    RunUnitTestsRequest,
    RunUnitTestsResponse,
    CheckGitStatusRequest,
    CheckGitStatusResponse,
)

# Load environment and OpenAI API key at module level
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found in environment. Please set it in your .env file."
    )
openai.api_key = OPENAI_API_KEY


class DevToolsAgent:
    """Agent for developer tool automation via function calling."""

    def run_formatter_linter(
        self, request: RunFormatterLinterRequest
    ) -> RunFormatterLinterResponse:
        """
        Run black and pylint on the given path using subprocess. Returns real output or error messages.
        - black runs on '.' by default
        - pylint runs on 'src' by default (to avoid linting .venv)
        Both have a 10 second timeout to prevent hanging.
        """
        black_path = request.path or "."
        pylint_path = request.path or "src"
        # Run black
        try:
            black_proc = subprocess.run(
                ["black", black_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            black_output = black_proc.stdout + black_proc.stderr
        except subprocess.TimeoutExpired:
            logging.exception("Timeout running black")
            black_output = "Error: black timed out after 10 seconds."
        except Exception as exc:  # pylint: disable=broad-except
            # Catch-all to ensure subprocess errors are logged and surfaced to user
            logging.exception("Error running black")
            black_output = f"Error running black: {exc}"
        # Run pylint (ignore .venv)
        try:
            pylint_proc = subprocess.run(
                ["pylint", "--ignore=.venv", pylint_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            pylint_output = pylint_proc.stdout + pylint_proc.stderr
        except subprocess.TimeoutExpired:
            logging.exception("Timeout running pylint")
            pylint_output = "Error: pylint timed out after 10 seconds."
        except Exception as exc:  # pylint: disable=broad-except
            # Catch-all to ensure subprocess errors are logged and surfaced to user
            logging.exception("Error running pylint")
            pylint_output = f"Error running pylint: {exc}"
        success = ("Error" not in black_output) and ("Error" not in pylint_output)
        return RunFormatterLinterResponse(
            success=success,
            black_output=black_output.strip(),
            pylint_output=pylint_output.strip(),
        )

    def run_unit_tests(self, request: RunUnitTestsRequest) -> RunUnitTestsResponse:
        """
        Run unit tests at the given path using unittest discover. Returns real output and parses summary.
        """
        test_path = request.test_path or "tests"
        try:
            proc = subprocess.run(
                ["python", "-m", "unittest", "discover", "-s", test_path],
                capture_output=True,
                text=True,
                check=False,
                timeout=30,
            )
            output = proc.stdout + proc.stderr
            # Parse summary and failed tests
            summary_match = re.search(r"(\d+ tests? in [\d.]+s)\)?", output)
            summary = summary_match.group(1) if summary_match else "Tests completed."
            failed_tests = []
            for line in output.splitlines():
                if line.startswith("FAIL:") or line.startswith("ERROR:"):
                    failed_tests.append(line.strip())
            success = proc.returncode == 0
        except subprocess.TimeoutExpired:
            logging.exception("Timeout running unit tests")
            return RunUnitTestsResponse(
                success=False,
                summary="Error: unit tests timed out after 30 seconds.",
                failed_tests=[],
            )
        except Exception as exc:  # pylint: disable=broad-except
            # Catch-all to ensure subprocess errors are logged and surfaced to user
            logging.exception("Error running unit tests")
            return RunUnitTestsResponse(
                success=False,
                summary=f"Error running unit tests: {exc}",
                failed_tests=[],
            )
        return RunUnitTestsResponse(
            success=success,
            summary=summary,
            failed_tests=failed_tests,
        )

    def check_git_status(
        self, _request: CheckGitStatusRequest
    ) -> CheckGitStatusResponse:
        """
        Check for uncommitted git files using git status --porcelain. Always uses '.' as the path.
        """
        path = "."
        try:
            proc = subprocess.run(
                ["git", "-C", path, "status", "--porcelain"],
                capture_output=True,
                text=True,
                check=False,
                timeout=10,
            )
            output = proc.stdout
            uncommitted_files = []
            for line in output.splitlines():
                parts = line.strip().split()
                if len(parts) == 2:
                    uncommitted_files.append(parts[1])
                elif len(parts) > 2:
                    uncommitted_files.append(parts[-1])
            has_uncommitted = len(uncommitted_files) > 0
        except subprocess.TimeoutExpired:
            logging.exception("Timeout running git status")
            return CheckGitStatusResponse(
                uncommitted_files=[],
                has_uncommitted=False,
            )
        except Exception:  # pylint: disable=broad-except
            # Catch-all to ensure subprocess errors are logged and surfaced to user
            logging.exception("Error running git status")
            return CheckGitStatusResponse(
                uncommitted_files=[],
                has_uncommitted=False,
            )
        return CheckGitStatusResponse(
            uncommitted_files=uncommitted_files,
            has_uncommitted=has_uncommitted,
        )

    def call_function(self, function_name: str, arguments: Dict[str, Any]) -> Any:
        """
        Dispatches a function call by name with validated arguments.
        """
        if function_name == "run_formatter_linter":
            request = RunFormatterLinterRequest(**arguments)
            return self.run_formatter_linter(request)
        if function_name == "run_unit_tests":
            request = RunUnitTestsRequest(**arguments)
            return self.run_unit_tests(request)
        if function_name == "check_git_status":
            request = CheckGitStatusRequest(**arguments)
            return self.check_git_status(request)
        raise ValueError(f"Unknown function: {function_name}")

    def run_openai_chat_loop(self, function_schemas, model: str = "gpt-4o") -> None:
        """
        Run an interactive OpenAI chat loop that supports function calling for developer tools.
        Loads the OpenAI API key from environment using dotenv for security and convenience.

        Args:
            function_schemas (list): List of OpenAI-compatible function schemas.
            model (str): OpenAI model name (default: 'gpt-4o').
        """
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a helpful developer assistant. "
                    "You can run code formatting, linting, unit tests, and check git status. "
                    "Use function calling when appropriate."
                ),
            }
        ]
        print("Type your request (or 'exit' to quit):")
        while True:
            user_input = input("You: ")
            if user_input.strip().lower() == "exit":
                break
            messages.append({"role": "user", "content": user_input})
            response = openai.chat.completions.create(
                model=model,
                messages=messages,
                functions=function_schemas,
                function_call="auto",
            )
            message = response.choices[0].message
            finish_reason = response.choices[0].finish_reason
            # Handle a chain of function calls until we get an assistant message
            while message.function_call:
                func_name = message.function_call.name
                func_args = message.function_call.arguments
                # print(f"\nOpenAI called function: {func_name} with args: {func_args}")
                args = json.loads(func_args)
                result = self.call_function(func_name, args)
                # Format result as JSON if possible
                if hasattr(result, "dict"):
                    result_json = json.dumps(result.dict(), indent=2)
                else:
                    result_json = (
                        json.dumps(result, indent=2)
                        if not isinstance(result, str)
                        else result
                    )
                # print(
                #     f"\n===== FUNCTION RESULT SUMMARY =====\n{result_json}\n==================================\n"
                # )
                messages.append(
                    {
                        "role": "function",
                        "name": func_name,
                        "content": result_json,
                    }
                )
                # Get the next response (could be another function call or assistant message)
                response = openai.chat.completions.create(
                    model=model,
                    messages=messages,
                    functions=function_schemas,
                    function_call="auto",
                )
                message = response.choices[0].message
                finish_reason = response.choices[0].finish_reason
            # Now we have an assistant message
            print(f"Assistant: {message.content}\n")
            messages.append({"role": "assistant", "content": message.content})
            if finish_reason == "stop":
                print("Assistant indicated conversation is complete. Exiting loop.")
                break
            print("\n--------------------\n")
