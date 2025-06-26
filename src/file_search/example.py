"""
Example script for interacting with the FileSearchAgent using command-line arguments.
"""

import sys
import os
from src.file_search.agent import FileSearchAgent

# Ensure the project root is in sys.path so 'src' can be imported when running this script directly.
# This is necessary because Python sets the working directory to the script's folder, not the project root,
# so 'src' would not be found without this adjustment.
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))


def main():
    """Run a file search Q&A session from the command line."""
    if len(sys.argv) < 3:
        print("Usage: python example.py <file_path> <question>")
        sys.exit(1)

    file_path = sys.argv[1]
    question = sys.argv[2]

    try:
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()
    except (OSError, UnicodeDecodeError) as e:
        # Catch file I/O and encoding errors only
        print(f"Error reading file: {e}")
        sys.exit(1)

    agent = FileSearchAgent()
    file_id = agent.upload_file(file_path, content)
    print(f"Uploaded file '{file_path}' with ID: {file_id}")

    try:
        answer = agent.answer_question(file_id, question)
        print(f"Q: {question}\nA: {answer}")
    except ValueError as e:
        # Only catch expected agent errors
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
