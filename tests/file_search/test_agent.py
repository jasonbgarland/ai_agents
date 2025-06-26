"""
Unit tests for FileSearchAgent chunking logic and edge cases.
"""

import unittest
from unittest.mock import patch
from src.file_search.agent import FileSearchAgent


class TestFileSearchAgentChunking(unittest.TestCase):
    def setUp(self):
        self.agent = FileSearchAgent()
        self.filename = "bigfile.txt"
        # Create a file with 3 chunks (chunk_size=10)
        self.content = "abcdefghij" * 3  # 30 chars
        self.file_id = self.agent.upload_file(self.filename, self.content)
        self.question = "What is in this file?"

    @patch("src.file_search.agent.get_openai_completion")
    def test_chunking_and_synthesis(self, mock_openai):
        # Simulate OpenAI returning the chunk number as the answer
        mock_openai.side_effect = [
            "Chunk 1 answer",
            "Chunk 2 answer",
            "Chunk 3 answer",
            "Synthesized answer",
        ]
        answer = self.agent.answer_question(self.file_id, self.question, chunk_size=10)
        self.assertEqual("Synthesized answer", answer)
        self.assertEqual(mock_openai.call_count, 4)
        # Check that the synthesis prompt includes all partial answers
        synthesis_prompt = mock_openai.call_args_list[-1][0][0]
        self.assertIn("Chunk 1 answer", synthesis_prompt)
        self.assertIn("Chunk 2 answer", synthesis_prompt)
        self.assertIn("Chunk 3 answer", synthesis_prompt)

    @patch("src.file_search.agent.get_openai_completion")
    def test_single_chunk(self, mock_openai):
        mock_openai.return_value = "Single chunk answer"
        answer = self.agent.answer_question(self.file_id, self.question, chunk_size=100)
        self.assertEqual("Single chunk answer", answer)
        self.assertEqual(mock_openai.call_count, 1)

    @patch("src.file_search.agent.get_openai_completion")
    def test_file_not_found(self, mock_openai):
        with self.assertRaises(ValueError):
            self.agent.answer_question("nonexistent_id", self.question)

    @patch("src.file_search.agent.get_openai_completion")
    def test_empty_file_content(self, mock_openai):
        file_id = self.agent.upload_file("empty.txt", "")
        mock_openai.return_value = "No content"
        answer = self.agent.answer_question(file_id, self.question)
        self.assertEqual("No content", answer)
        self.assertEqual(mock_openai.call_count, 1)

    @patch("src.file_search.agent.get_openai_completion")
    def test_empty_question(self, mock_openai):
        mock_openai.return_value = "No question provided"
        answer = self.agent.answer_question(self.file_id, "")
        self.assertEqual("No question provided", answer)
        self.assertEqual(mock_openai.call_count, 1)

    @patch("src.file_search.agent.get_openai_completion")
    def test_unicode_content(self, mock_openai):
        unicode_content = "😀 Привет こんにちは مرحبا"
        file_id = self.agent.upload_file("unicode.txt", unicode_content)
        mock_openai.return_value = "Unicode handled"
        answer = self.agent.answer_question(file_id, self.question)
        self.assertEqual("Unicode handled", answer)
        self.assertEqual(mock_openai.call_count, 1)

    @patch("src.file_search.agent.get_openai_completion")
    def test_many_chunks(self, mock_openai):
        # 100 chunks of 10 chars each
        content = "abcdefghij" * 100
        file_id = self.agent.upload_file("huge.txt", content)
        # 100 partial answers + 1 synthesis
        mock_openai.side_effect = [f"Chunk {i+1}" for i in range(100)] + ["Synthesized"]
        answer = self.agent.answer_question(file_id, self.question, chunk_size=10)
        self.assertEqual("Synthesized", answer)
        self.assertEqual(mock_openai.call_count, 101)

    @patch("src.file_search.agent.get_openai_completion")
    def test_custom_chunk_size(self, mock_openai):
        # 25 chars, chunk_size=5 -> 5 chunks
        content = "abcde" * 5
        file_id = self.agent.upload_file("custom.txt", content)
        mock_openai.side_effect = [f"Chunk {i+1}" for i in range(5)] + ["Synthesized"]
        answer = self.agent.answer_question(file_id, self.question, chunk_size=5)
        self.assertEqual("Synthesized", answer)
        self.assertEqual(mock_openai.call_count, 6)

    @patch("src.file_search.agent.get_openai_completion")
    def test_multiple_files(self, mock_openai):
        file_id2 = self.agent.upload_file("other.txt", "other content")
        mock_openai.return_value = "Other file answer"
        answer = self.agent.answer_question(file_id2, self.question)
        self.assertEqual("Other file answer", answer)
        self.assertEqual(mock_openai.call_count, 1)

    @patch("src.file_search.agent.get_openai_completion")
    def test_answer_question_multiple_files(self, mock_openai):
        # Simulate two files, each with a single chunk
        file_id2 = self.agent.upload_file("frog2.txt", "Another frog story.")
        mock_openai.side_effect = [
            "Barley is a solitary frog.",
            "Another frog is also solitary.",
            "Both stories feature solitary frogs.",
        ]
        result = self.agent.answer_question_multiple_files(
            [self.file_id, file_id2], self.question
        )
        self.assertIn("Both stories feature solitary frogs.", result)
        self.assertEqual(mock_openai.call_count, 3)

    @patch("src.file_search.agent.get_openai_completion")
    def test_answer_question_multiple_files_empty(self, mock_openai):
        # Should return a clear message if no file IDs are provided
        result = self.agent.answer_question_multiple_files([], self.question)
        self.assertIn("No answers could be generated", result)

    @patch("src.file_search.agent.get_openai_completion")
    def test_answer_question_multiple_files_mixed_errors(self, mock_openai):
        # One valid, one invalid file ID
        file_id2 = self.agent.upload_file("frog2.txt", "Another frog story.")
        mock_openai.side_effect = [
            "Barley is a solitary frog.",
            "Both stories feature solitary frogs.",
        ]
        result = self.agent.answer_question_multiple_files(
            [self.file_id, "bad_id"], self.question
        )
        self.assertIn("File ID bad_id: File not found.", result)
        self.assertNotIn("Both stories feature solitary frogs.", result)

    @patch("src.file_search.agent.get_openai_completion")
    def test_chunking_exact_multiple(self, mock_openai):
        # File size is exactly 20, chunk_size=10 -> 2 chunks
        content = "abcdefghij" * 2
        file_id = self.agent.upload_file("exact.txt", content)
        mock_openai.side_effect = ["Chunk 1", "Chunk 2", "Synthesized"]
        answer = self.agent.answer_question(file_id, self.question, chunk_size=10)
        self.assertEqual("Synthesized", answer)
        self.assertEqual(mock_openai.call_count, 3)

    @patch("src.file_search.agent.get_openai_completion")
    def test_chunking_just_over_boundary(self, mock_openai):
        # File size is 11, chunk_size=10 -> 2 chunks
        content = "abcdefghijz"
        file_id = self.agent.upload_file("over.txt", content)
        mock_openai.side_effect = ["Chunk 1", "Chunk 2", "Synthesized"]
        answer = self.agent.answer_question(file_id, self.question, chunk_size=10)
        self.assertEqual("Synthesized", answer)
        self.assertEqual(mock_openai.call_count, 3)

    @patch("src.file_search.agent.get_openai_completion")
    def test_many_files(self, mock_openai):
        # 10 files, each with a single chunk
        file_ids = [
            self.agent.upload_file(f"f{i}.txt", f"content {i}") for i in range(10)
        ]
        mock_openai.side_effect = [f"A{i}" for i in range(10)] + ["Synthesized"]
        answer = self.agent.answer_question_multiple_files(file_ids, self.question)
        self.assertEqual("Synthesized", answer)
        self.assertEqual(mock_openai.call_count, 11)

    def test_upload_file_from_path_non_utf8(self):
        import tempfile
        import os

        # Write a file with non-UTF-8 bytes
        with tempfile.NamedTemporaryFile(delete=False) as tmp:
            tmp.write(b"\xff\xfe\xfd")
            tmp_path = tmp.name
        agent = FileSearchAgent()
        with self.assertRaises(ValueError):
            agent.upload_file_from_path(tmp_path)
        os.remove(tmp_path)

    def test_duplicate_file_uploads(self):
        file_id1 = self.agent.upload_file("dupe.txt", "same content")
        file_id2 = self.agent.upload_file("dupe.txt", "same content")
        self.assertNotEqual(file_id1, file_id2)
        self.assertIn(file_id1, self.agent.files)
        self.assertIn(file_id2, self.agent.files)


if __name__ == "__main__":
    unittest.main()
