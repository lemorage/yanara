import importlib
import os
from pathlib import Path

from yanara.globals import client


def load_all_tools():
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
