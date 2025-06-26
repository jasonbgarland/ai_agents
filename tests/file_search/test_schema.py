"""
Unit tests for File Search Agent schemas.
"""

import unittest
from src.file_search import schema


class TestFileSearchSchemas(unittest.TestCase):
    def test_file_upload_request(self):
        req = schema.FileUploadRequest(filename="test.txt", content="Hello world!")
        self.assertEqual("test.txt", req.filename)
        self.assertEqual("Hello world!", req.content)

    def test_question_request(self):
        req = schema.QuestionRequest(
            question="What is this file about?", file_id="abc123"
        )
        self.assertEqual("What is this file about?", req.question)
        self.assertEqual("abc123", req.file_id)

    def test_answer_response(self):
        resp = schema.AnswerResponse(answer="This file is a greeting.")
        self.assertEqual("This file is a greeting.", resp.answer)

    def test_error_response(self):
        resp = schema.ErrorResponse(error="File not found.")
        self.assertEqual("File not found.", resp.error)


if __name__ == "__main__":
    unittest.main()
