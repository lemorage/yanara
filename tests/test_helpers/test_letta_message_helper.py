from datetime import datetime, timezone
import json
import os
from unittest.mock import patch
import warnings

import pytest

warnings.filterwarnings("ignore", category=DeprecationWarning)

from letta.schemas.letta_message import (
    AssistantMessage,
    FunctionCall,
    FunctionCallMessage,
    FunctionReturn,
    InternalMonologue,
)

from yanara.helpers.letta_message_helper import (
    extract_file_path_from_function_return,
    extract_message_from_function_call,
)


@pytest.mark.unit
def test_extract_message_from_function_call_valid_message():
    # Arrange
    messages = [
        InternalMonologue(
            id="message-5696a2b5-4019-4a4e-96a4-0793041acb35",
            date=datetime(2024, 11, 26, 12, 46, 14, 771577, tzinfo=timezone.utc),
            message_type="internal_monologue",
            internal_monologue="Sarah just logged in for the first time and said hello. Quick, think of a warm, friendly, emoji-loaded response. Let's make her feel welcome! I should also remember to show eagerness in assisting her with anything she might need.",
        ),
        FunctionCallMessage(
            id="message-5696a2b5-4019-4a4e-96a4-0793041acb35",
            date=datetime(2024, 11, 26, 12, 46, 14, 771577, tzinfo=timezone.utc),
            message_type="function_call",
            function_call=FunctionCall(
                id="func-call-1",
                function_call_id="function-call-id-1",
                name="send_message",
                arguments=json.dumps({"message": "Hello there, Sarah!"}),
            ),
        ),
        FunctionReturn(
            id="message-3c5ba1dc-1030-4caa-b6ca-39f23c034c36",
            date=datetime(2024, 11, 26, 12, 46, 14, 771882, tzinfo=timezone.utc),
            message_type="function_return",
            function_call_id="function-call-id-1",
            function_return=json.dumps({"status": "OK", "message": "None", "time": "2024-11-26 12:46:14 PM UTC+0000"}),
            status="success",
        ),
    ]

    expected_result = "Hello there, Sarah!"

    # Act
    result = extract_message_from_function_call(messages)

    # Assert
    assert result == expected_result


@pytest.mark.unit
def test_extract_message_from_function_call_invalid_json():
    # Arrange
    invalid_function_call = FunctionCall(
        id="call-2", function_call_id="function-call-id-2", name="send_message", arguments="{invalid_json}"
    )
    messages = [
        FunctionCallMessage(
            id="msg-2",
            date=datetime.now(timezone.utc),
            message_type="function_call",
            function_call=invalid_function_call,
        )
    ]

    # Act
    result = extract_message_from_function_call(messages)

    # Assert
    assert result is None


@pytest.mark.unit
def test_extract_message_from_function_call_wrong_function_name():
    # Arrange
    wrong_function_call = FunctionCall(
        id="call-3",
        function_call_id="function-call-id-3",
        name="other_function",
        arguments=json.dumps({"message": "Hello!"}),
    )
    messages = [
        FunctionCallMessage(
            id="msg-3", date=datetime.now(timezone.utc), message_type="function_call", function_call=wrong_function_call
        )
    ]

    # Act
    result = extract_message_from_function_call(messages)

    # Assert
    assert result is None


@pytest.mark.unit
def test_extract_file_path_from_function_return_valid_path(tmp_path):
    # Arrange
    valid_file = tmp_path / "test_file.txt"
    valid_file.write_text("test content")
    function_return = FunctionReturn(
        id="message-1",
        date=datetime.now(timezone.utc),
        message_type="function_return",
        function_call_id="function-call-id-1",
        function_return=json.dumps({"message": str(valid_file)}),
        status="success",
    )
    function_returns = [function_return]

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (True, str(valid_file))


@pytest.mark.unit
def test_extract_file_path_from_function_return_invalid_json():
    # Arrange
    function_return = FunctionReturn(
        id="message-2",
        date=datetime.now(timezone.utc),
        message_type="function_return",
        function_call_id="function-call-id-2",
        function_return="{invalid_json}",
        status="error",
    )
    function_returns = [function_return]

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (False, None)


@pytest.mark.unit
def test_extract_file_path_from_function_return_no_message_field():
    # Arrange
    function_return = FunctionReturn(
        id="message-3",
        date=datetime.now(timezone.utc),
        message_type="function_return",
        function_call_id="function-call-id-3",
        function_return=json.dumps({"other_field": "value"}),
        status="success",
    )
    function_returns = [function_return]

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (False, None)


@pytest.mark.unit
def test_extract_file_path_from_function_return_message_not_a_file():
    # Arrange
    non_existent_file = "/path/to/nonexistent/file.txt"
    function_return = FunctionReturn(
        id="message-4",
        date=datetime.now(timezone.utc),
        message_type="function_return",
        function_call_id="function-call-id-4",
        function_return=json.dumps({"message": non_existent_file}),
        status="success",
    )
    function_returns = [function_return]

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (False, None)


@pytest.mark.unit
def test_extract_file_path_from_function_return_no_function_return_messages():
    # Arrange
    function_returns = []

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (False, None)


@pytest.mark.unit
def test_extract_file_path_from_function_return_empty_message_field():
    # Arrange
    function_return = FunctionReturn(
        id="message-5",
        date=datetime.now(timezone.utc),
        message_type="function_return",
        function_call_id="function-call-id-5",
        function_return=json.dumps({"message": ""}),
        status="success",
    )
    function_returns = [function_return]

    # Act
    result = extract_file_path_from_function_return(function_returns)

    # Assert
    assert result == (False, None)
