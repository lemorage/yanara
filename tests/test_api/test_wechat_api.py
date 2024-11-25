import asyncio
from typing import Any, Dict, List

import pytest

from yanara.api.wechat_api.wechat_message_worker import WeChatMessageWorker


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "messages,expected_usernames",
    [
        # Test Case 1: Multiple messages
        (
            [
                {
                    "msg_id": 1127841265,
                    "from_user_name": {"str": "35019477707@chatroom"},
                    "to_user_name": {"str": "wxid_fdsoz331br5g22"},
                    "msg_type": 1,
                    "content": {"str": "qoitaaxb:\n好的[Facepalm] 来"},
                    "status": 3,
                    "img_status": 1,
                    "img_buf": {"len": 0},
                    "create_time": 1732066896,
                    "msg_source": "<msgsource></msgsource>",
                    "push_content": "六一三 : 好的[Facepalm] 来",
                    "new_msg_id": 2414659179099175024,
                },
                {
                    "msg_id": 873989190,
                    "from_user_name": {"str": "35019477707@chatroom"},
                    "to_user_name": {"str": "wxid_fdsoz331br5g22"},
                    "msg_type": 1,
                    "content": {"str": "qoitaaxb:\n@miao.\u2005"},
                    "status": 3,
                    "img_status": 1,
                    "img_buf": {"len": 0},
                    "create_time": 1732066899,
                    "msg_source": "<msgsource></msgsource>",
                    "push_content": "六一三 mentioned you in a group chat.",
                    "new_msg_id": 6270614409704083722,
                },
            ],
            ["35019477707@chatroom"],
        ),
        # Test Case 2: Single message
        (
            [
                {
                    "msg_id": 1431275716,
                    "from_user_name": {"str": "wxid_fdsoz331br5g22"},
                    "to_user_name": {"str": "35019477707@chatroom"},
                    "msg_type": 1,
                    "content": {"str": "好了[OK]"},
                    "status": 3,
                    "img_status": 1,
                    "img_buf": {"len": 0},
                    "create_time": 1732067357,
                    "msg_source": "<msgsource></msgsource>",
                    "new_msg_id": 7054960764588121913,
                }
            ],
            ["wxid_fdsoz331br5g22"],
        ),
        # Test Case 3: No messages
        ([], []),
    ],
)
async def test_process_messages(messages: List[Dict[str, Any]], expected_usernames: List[str], mocker) -> None:
    """Test the process_messages method with different scenarios."""
    # Arrange
    worker = WeChatMessageWorker(messages, wechat_account=mocker.Mock())
    account_key = "test_account_key"

    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_messages(account_key)

    # Assert
    if messages:
        usernames = worker.extract_usernames()
        assert usernames == expected_usernames

        for username in usernames:
            assert mock_route_message.called
    else:
        assert not mock_route_message.called


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_messages_all_messages_from_one_user(mocker) -> None:
    """Test that all messages from a user are processed if multiple messages exist."""
    # Arrange
    messages = [
        {
            "msg_id": 1127841265,
            "from_user_name": {"str": "35019477707@chatroom"},
            "to_user_name": {"str": "wxid_fdsoz331br5g22"},
            "msg_type": 1,
            "content": {"str": "Message 1 from user 35019477707@chatroom"},
            "status": 3,
            "img_status": 1,
            "img_buf": {"len": 0},
            "create_time": 1732066896,
            "msg_source": "<msgsource></msgsource>",
            "push_content": "Push content 1",
            "new_msg_id": 2414659179099175024,
        },
        {
            "msg_id": 873989191,
            "from_user_name": {"str": "35019477707@chatroom"},
            "to_user_name": {"str": "wxid_fdsoz331br5g22"},
            "msg_type": 1,
            "content": {"str": "Message 2 from user 35019477707@chatroom"},
            "status": 3,
            "img_status": 1,
            "img_buf": {"len": 0},
            "create_time": 1732066900,
            "msg_source": "<msgsource></msgsource>",
            "push_content": "Push content 2",
            "new_msg_id": 6270614409704083722,
        },
    ]
    worker = WeChatMessageWorker(messages, wechat_account=mocker.Mock())
    account_key = "test_account_key"

    # Mock the route_message method to track calls
    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_messages(account_key)

    # Assert
    assert mock_route_message.call_count == 2

    # Ensure it processes both messages
    mock_route_message.assert_any_call(
        "35019477707@chatroom", "wxid_fdsoz331br5g22", "Message 1 from user 35019477707@chatroom", "Push content 1"
    )
    mock_route_message.assert_any_call(
        "35019477707@chatroom", "wxid_fdsoz331br5g22", "Message 2 from user 35019477707@chatroom", "Push content 2"
    )
