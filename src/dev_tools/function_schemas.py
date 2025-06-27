"""
OpenAI function schemas for DevToolsAgent, generated from Pydantic models.
"""

import json

from src.dev_tools.schema import (
    RunFormatterLinterRequest,
    RunUnitTestsRequest,
    CheckGitStatusRequest,
)


def get_openai_function_schemas():
    """
    Returns a list of OpenAI function schemas for DevToolsAgent.
    """
    return [
        {
            "name": "run_formatter_linter",
            "description": "Run black and pylint on the given path.",
            "parameters": RunFormatterLinterRequest.model_json_schema(),
        },
        {
            "name": "run_unit_tests",
            "description": "Run unit tests at the given path.",
            "parameters": RunUnitTestsRequest.model_json_schema(),
        },
        {
            "name": "check_git_status",
            "description": "Check for uncommitted git files.",
            "parameters": CheckGitStatusRequest.model_json_schema(),
        },
    ]


if __name__ == "__main__":
    schemas = get_openai_function_schemas()
    print(json.dumps(schemas, indent=2))
