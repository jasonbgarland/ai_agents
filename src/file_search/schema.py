"""
Pydantic schemas for File Search Agent requests and responses.
"""

from pydantic import BaseModel, Field


class FileUploadRequest(BaseModel):
    """Request model for uploading a file to the File Search Agent."""

    filename: str = Field(..., description="Name of the uploaded file")
    content: str = Field(..., description="File content as string (decoded)")


class QuestionRequest(BaseModel):
    """Request model for asking a question about a file."""

    question: str = Field(
        ..., description="User's natural language question about the file"
    )
    file_id: str = Field(..., description="Unique identifier for the uploaded file")


class AnswerResponse(BaseModel):
    """Response model for an answer to a user's question."""

    answer: str = Field(..., description="Agent's answer to the user's question")


class ErrorResponse(BaseModel):
    """Response model for error messages from the File Search Agent."""

    error: str = Field(..., description="Error message if something goes wrong")
