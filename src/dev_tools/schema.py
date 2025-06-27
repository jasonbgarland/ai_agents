"""
Schemas for developer tool function calling agent.
"""

from typing import List, Optional
from pydantic import BaseModel, Field


class RunFormatterLinterRequest(BaseModel):
    """Request model for running formatter and linter."""

    path: Optional[str] = Field(
        None, description="Path to format/lint. Defaults to project root."
    )


class RunFormatterLinterResponse(BaseModel):
    """Response model for running formatter and linter."""

    success: bool
    black_output: str
    pylint_output: str


class RunUnitTestsRequest(BaseModel):
    """Request model for running unit tests."""

    test_path: Optional[str] = Field(
        None, description="Path to test(s). Defaults to all tests."
    )


class RunUnitTestsResponse(BaseModel):
    """Response model for running unit tests."""

    success: bool
    summary: str
    failed_tests: List[str] = []


class CheckGitStatusRequest(BaseModel):
    """Request model for checking git status."""

    # No fields required


class CheckGitStatusResponse(BaseModel):
    """Response model for checking git status."""

    uncommitted_files: List[str]
    has_uncommitted: bool
