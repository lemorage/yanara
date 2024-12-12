import importlib
import os
from pathlib import Path

from letta import LocalClient, RESTClient
from rich import print

from yanara.globals import client


def load_all_tools(client: LocalClient | RESTClient):
    """
    Dynamically loads all callable tools (functions) from the `tools` directory.

    This function scans the `tools` directory and its subdirectories for Python modules,
    dynamically imports them, and collects all callable functions defined within these modules.
    It then registers these functions as tools using the `client` object.

    Workflow:
    1. Define the `tools` directory path relative to the current file.
    2. Traverse the directory recursively to locate all `.py` files (excluding `__init__.py`).
    3. Dynamically import each module and collect all callable attributes (functions).
    4. Register each callable function as a tool with the `client`.
    """
    # Define the path to the tools directory
    tools_dir = Path(__file__).parent / "tools"
    tools = []

    # Recursively find and load all Python modules in the tools directory
    for root, _, files in os.walk(tools_dir):
        for file in files:
            if file.endswith(".py") and not file.startswith("__"):  # Ignore __init__.py
                module_path = os.path.relpath(os.path.join(root, file), tools_dir.parent)
                module_name = module_path.replace(os.sep, ".").rstrip(".py")

                module = importlib.import_module(module_name)

                for attr_name in dir(module):
                    attr = getattr(module, attr_name)
                    if callable(attr):  # Filter out functions
                        tools.append(attr)

    # Register each tool with the client
    for tool_function in tools:
        tool = client.create_tool(tool_function)
        print(f"Registered tool: {tool.name} ({tool.id})")


def cleanup(client: LocalClient | RESTClient, agent_name: str = None, agent_uuid: str = None):
    """
    Deletes a specific agent from the system by its name or unique identifier (UUID).

    This function iterates through all agents managed by the given `client`,
    identifies the agent using either `agent_name` or `agent_uuid`, and deletes it.
    If neither `agent_name` nor `agent_uuid` is provided, the function does nothing.

    Args:
        client (LocalClient | RESTClient): The client instance used to interact with the agents.
        agent_name (str, optional): The name of the agent to be deleted. Defaults to None.
        agent_uuid (str, optional): The unique identifier (UUID) of the agent to be deleted. Defaults to None.
    """
    if not agent_name and not agent_uuid:
        return
    for agent_state in client.list_agents():
        if agent_state.name == agent_name or agent_state.id == agent_uuid:
            client.delete_agent(agent_id=agent_state.id)
            print(f"Deleted agent: {agent_state.name} with ID {str(agent_state.id)}")
