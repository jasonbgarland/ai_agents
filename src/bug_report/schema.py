"""
This module defines the schema for bug reports, including the severity levels
and the structure of a bug report using Pydantic models.

Classes:
    Severity: An enumeration representing the severity levels of a bug.
    BugReport: A Pydantic model representing the structure of a bug report.

Enums:
    Severity: Defines severity levels as 'low', 'medium', and 'high'.

Models:
    BugReport: Contains fields for the affected project, error message, steps
    to reproduce the issue, and the severity of the bug.
"""

from enum import Enum

from typing import List, Optional, Union

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """
    An enumeration representing the severity levels of a bug report.
    Attributes:
        LOW (str): Represents a low severity level.
        MEDIUM (str): Represents a medium severity level.
        HIGH (str): Represents a high severity level.
    """

    LOW = "Low"
    MEDIUM = "Medium"
    HIGH = "High"


class BugReport(BaseModel):
    """
    BugReport model represents the structure of a bug report.
    """

    project_affected: Optional[str] = Field(
        default=None,
        description="Name of the affected project or component.",
        serialization_alias="Project Affected",
    )
    error_message: Optional[str] = Field(
        default=None,
        description="Error message or description of the problem.",
        serialization_alias="Error Message",
    )
    steps_to_reproduce: Optional[List[str]] = Field(
        default=None,
        description="List of steps to reproduce the issue.",
        serialization_alias="Steps To Reproduce",
    )
    severity: Optional[Union[Severity, str]] = Field(
        default=None, description="Severity of the bug.", serialization_alias="Severity"
    )
