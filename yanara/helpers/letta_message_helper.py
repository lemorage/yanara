import base64
import datetime
import json
import os

from letta.schemas.letta_message import (
    AssistantMessage,
    FunctionCall,
    FunctionCallMessage,
    FunctionReturn,
    InternalMonologue,
    LettaMessage,
    SystemMessage,
    UserMessage,
)


def extract_message_from_function_call(messages: list[LettaMessage]) -> str | None:
    """
    Extracts a message string from a list of LettaMessage objects.

    This function looks for a FunctionCallMessage where the `function_call.name`
    is "send_message", attempts to parse the `function_call.arguments` as JSON,
    and retrieves the "message" field if present.

    Args:
        messages (list[LettaMessage]): A list of messages to search through.

    Returns:
        str | None: The extracted message string if found, or None if no
        valid message could be extracted.
    """
    for message in messages:
        # Check if the message is a FunctionCallMessage with the correct function name
        if isinstance(message, FunctionCallMessage) and message.function_call.name == "send_message":
            try:
                arguments = json.loads(message.function_call.arguments)
                return arguments.get("message")
            except json.JSONDecodeError:
                print("Error parsing arguments as JSON")
    return None


def extract_file_path_from_function_return(function_returns: list[LettaMessage]) -> tuple[bool, str | None]:
    """
    Extracts and validates a file path from a list of LettaMessage objects.

    This function looks for a FunctionReturn object, attempts to parse its
    `function_return` field as JSON, and checks if the "message" field is a valid
    file path.

    Args:
        function_returns (list[LettaMessage]): A list of function return messages.

    Returns:
        tuple[bool, str | None]: A tuple containing a boolean and a string.
            - The boolean is True if a valid file path was found; False otherwise.
            - The string is the valid file path if found; None otherwise.
    """
    for return_message in function_returns:
        if isinstance(return_message, FunctionReturn):
            try:
                function_return = json.loads(return_message.function_return)
                # Check if the 'message' field exists and contains a valid file path
                message = function_return.get("message")
                if message and isinstance(message, str):
                    if os.path.isfile(message):
                        return True, message  # Return True and the file path
            except json.JSONDecodeError:
                pass
    return False, None
