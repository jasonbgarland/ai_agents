"""
Agent for collecting bug report details over multiple conversation turns.

Responsibilities:
- Guide the user through each required field
- Store and update conversation state
- Validate and assemble a BugReport object
"""

import os
from typing import Dict, Any, Optional, Tuple

import openai
from dotenv import load_dotenv

from src.bug_report.schema import BugReport, Severity

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY")


class BugReportAgent:
    """Conversational agent for collecting structured bug reports over multiple turns."""

    def __init__(self):
        # Initialize conversation state
        self.state: Dict[str, Any] = {}
        # Define the fields to collect in order.
        # This is so that we can prompt the user with the correct questions later.
        self.fields = [
            "project_affected",
            "error_message",
            "steps_to_reproduce",
            "severity",
        ]
        self.current_field_index = 0

    def get_next_prompt(self) -> Optional[str]:
        """Return the next prompt for the user, or None if complete."""
        if self.current_field_index >= len(self.fields):
            return None
        field = self.fields[self.current_field_index]
        prompts = {
            "project_affected": "What project or component is affected?",
            "error_message": "What is the error message or problem?",
            "steps_to_reproduce": "List the steps to reproduce the issue (one per line or separated by ';').",
            "severity": "What is the severity? (Low, Medium, High)",
        }
        return prompts[field]

    def update_state(self, user_input: str) -> None:
        """Update the state with the user's input for the current field."""
        field = self.fields[self.current_field_index]
        if field == "steps_to_reproduce":
            # Split steps by line or semicolon
            steps = [
                step.strip()
                for step in user_input.replace(";", "\n").split("\n")
                if step.strip()
            ]
            self.state[field] = steps
        elif field == "severity":
            # Normalize and validate severity
            value = user_input.strip().capitalize()
            if value not in [s.value for s in Severity]:
                raise ValueError(f"Invalid severity: {user_input}")
            self.state[field] = value
        else:
            self.state[field] = user_input.strip()
        self.current_field_index += 1

    def is_complete(self) -> bool:
        """Check if all fields have been collected."""
        return self.current_field_index >= len(self.fields)

    def assemble_report(self) -> BugReport:
        """Assemble and return the BugReport object from state."""
        if not self.is_complete():
            raise ValueError("Bug report is not complete.")
        return BugReport(
            project_affected=self.state["project_affected"],
            error_message=self.state["error_message"],
            steps_to_reproduce=self.state["steps_to_reproduce"],
            severity=Severity(self.state["severity"]),
        )

    def process_turn(self, user_input: str) -> Tuple[BugReport, str, bool]:
        """
        Process a turn in the bug report conversation.
        Args:
            user_input (str): The latest user message.
        Returns:
            Tuple containing:
                - updated_state (BugReport): The updated bug report as a Pydantic model.
                - prompt (str): Message to send to the user (acknowledges filled fields, requests missing ones).
                - is_complete (bool): True if all required fields are filled.
        """
        # Prepare system prompt with current state
        system_message = (
            "You are a helpful assistant collecting bug reports. "
            "Here is the current bug report state (fields may be missing):\n"
            f"{self.state}\n"
            "Update the bug report with any new information from the user's message. "
            "Return the updated bug report in the expected format."
        )

        try:
            # Call OpenAI API to parse and update the state
            response = openai.responses.parse(
                model="gpt-4.1-nano",
                input=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_input},
                ],
                text_format=BugReport,
            )
            # Parse the output into a BugReport model
            bug_report = response.output_parsed
        # pylint: disable=broad-except
        except (
            Exception
        ) as exc:  # Many possible OpenAI errors: rate limit, connection, validation, etc.
            # Return a partial BugReport (with possibly incomplete fields) and a helpful prompt
            partial_report = BugReport()
            prompt = f"There was a problem parsing your input: {exc}"
            return partial_report, prompt, False

        # If severity is missing and all other fields are present, set to Medium and mark as complete
        missing = [
            field
            for field in BugReport.model_fields.keys()
            if getattr(bug_report, field) in (None, "", [], {})
        ]
        filled = [
            field
            for field in BugReport.model_fields.keys()
            if getattr(bug_report, field) not in (None, "", [], {})
        ]
        if missing == ["severity"]:
            bug_report.severity = Severity.MEDIUM
            prompt = (
                "All required information has been collected. Since no severity was specified, "
                "it has been set to 'Medium' by default. Here is your bug report:\n"
                + str(bug_report)
            )
            is_complete = True
            return bug_report, prompt, is_complete

        # If any required field is missing, do not mark as complete
        if missing:
            prompt = (
                f"I have the following information: {', '.join(filled)}. "
                f"Please provide: {', '.join(missing)}."
            )
            is_complete = False
            return bug_report, prompt, is_complete

        # If severity is present but invalid, prompt for a valid value and do not mark as complete
        if hasattr(bug_report, "severity") and bug_report.severity not in [
            Severity.LOW,
            Severity.MEDIUM,
            Severity.HIGH,
        ]:
            prompt = (
                f"The provided severity '{bug_report.severity}' is not valid. "
                "Please specify one of: Low, Medium, or High."
            )
            is_complete = False
            return bug_report, prompt, is_complete

        # If all fields are present and valid, mark as complete
        prompt = "Thank you! All required information has been collected.\n"
        is_complete = True
        return bug_report, prompt, is_complete

    def report_bug(self):
        """
        Run the full bug report collection process interactively in the console.
        Prompts the user for input, processes each turn, and outputs the final report.
        """
        print("Welcome to the Bug Report Agent! Type your bug details below.")
        is_complete = False
        state = None
        while not is_complete:
            user_input = input("You: ")
            state, prompt, is_complete = self.process_turn(user_input)
            self.state = (
                state.model_dump()
            )  # Store as dict for backward compatibility if needed
            print(f"Agent: {prompt}\n")
        print("Final structured bug report:")
        data = state.model_dump(by_alias=True)
        for key, value in data.items():
            if key == "Steps To Reproduce" and isinstance(value, list):
                print(f"{key}:")
                for i, step in enumerate(value, 1):
                    print(f"  {i}. {step}")
            else:
                print(f"{key}: {value}")
