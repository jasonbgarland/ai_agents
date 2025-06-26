"""
File Search Agent: Handles file upload and natural language Q&A using OpenAI.
"""

import uuid
from src.openai_client import get_openai_completion


class FileSearchAgent:
    """
    Agent for answering natural language questions about uploaded files using OpenAI.
    Uses chunking to handle files larger than the OpenAI context window.
    """

    def __init__(self):
        # In-memory storage for uploaded files: {file_id: (filename, content)}
        self.files = {}

    def upload_file(self, filename: str, content: str) -> str:
        """
        Stores the uploaded file and returns a unique file ID.
        """
        file_id = str(uuid.uuid4())
        self.files[file_id] = (filename, content)
        return file_id

    def upload_file_from_path(self, file_path: str) -> str:
        """
        Reads a file from disk, verifies it exists and is readable, and uploads it.
        Raises ValueError if the file cannot be read.
        """
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
        except (OSError, UnicodeDecodeError) as e:
            # Catch file I/O and encoding errors only
            raise ValueError(f"Error reading file '{file_path}': {e}") from e
        return self.upload_file(file_path, content)

    def answer_question(
        self, file_id: str, question: str, chunk_size: int = 8000
    ) -> str:
        """
        Answers a question about the uploaded file using OpenAI.
        If the file is too large, splits it into chunks and aggregates answers.
        """
        if file_id not in self.files:
            raise ValueError("File not found.")
        filename, content = self.files[file_id]
        # Split content into chunks to fit within OpenAI's context window
        chunks = [
            content[i : i + chunk_size] for i in range(0, len(content), chunk_size)
        ]
        partial_answers = []
        for idx, chunk in enumerate(chunks):
            # Each chunk is processed independently
            prompt = (
                f"You are an assistant helping a user with questions about a file.\n"
                f"File name: {filename}\n"
                f"File content (part {idx+1}):\n{chunk}\n"
                f"Question: {question}\n"
                f"Answer:"
            )
            answer = get_openai_completion(prompt)
            partial_answers.append(answer)
        # Synthesize a final answer from all partial answers
        if len(partial_answers) == 1:
            return partial_answers[0]
        synthesis_prompt = (
            "Here are several answers to the same question from different parts of a file:\n"
            + "\n".join(partial_answers)
            + "\nPlease synthesize a single, comprehensive answer."
        )
        final_answer = get_openai_completion(synthesis_prompt)
        return final_answer

    def answer_question_multiple_files(
        self, file_ids: list[str], question: str, chunk_size: int = 8000
    ) -> str:
        """
        Answers a question about multiple uploaded files, synthesizing a single response.
        If any file fails, the error is surfaced to the user and not included in the synthesis.
        """
        partial_answers = []
        errors = []
        for file_id in file_ids:
            try:
                answer = self.answer_question(file_id, question, chunk_size=chunk_size)
                filename = self.files[file_id][0]
                partial_answers.append(f"File: {filename}\nAnswer: {answer}")
            except ValueError as e:
                # Only catch expected file/question errors
                errors.append(f"File ID {file_id}: {e}")
        if errors:
            return "\n".join(errors)
        if not partial_answers:
            return "No answers could be generated."
        if len(partial_answers) == 1:
            return partial_answers[0]
        synthesis_prompt = (
            "Here are answers to the same question from different files:\n"
            + "\n".join(partial_answers)
            + "\nPlease synthesize a single, comprehensive answer."
        )
        return get_openai_completion(synthesis_prompt)
