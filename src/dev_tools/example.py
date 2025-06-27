"""
Example entry point for DevToolsAgent OpenAI function calling demo.
Run this script to interact with the agent and see function calling in action.
"""

from src.dev_tools.agent import DevToolsAgent
from src.dev_tools.function_schemas import get_openai_function_schemas


def main():
    """
    Minimal demo: instantiate the agent, load schemas, and start the OpenAI chat loop.
    """
    agent = DevToolsAgent()
    function_schemas = get_openai_function_schemas()
    agent.run_openai_chat_loop(function_schemas)


if __name__ == "__main__":
    main()
