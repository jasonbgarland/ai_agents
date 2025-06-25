"""
Example script for interacting with the BugReportAgent in a multi-turn conversation.
"""

from src.bug_report.agent import BugReportAgent


def main():
    """Run an interactive example session with the BugReportAgent."""
    print("Welcome to the Bug Report Agent! Type your bug details below.")
    agent = BugReportAgent()
    agent.report_bug()


if __name__ == "__main__":
    main()
