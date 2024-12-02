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


@pytest.mark.unit
def test_has_incoming_message_all_type_1():
    """Test has_incoming_message when all messages are type 1."""
    # Arrange
    messages = [
        {"msg_type": 1, "from_user_name": {"str": "user1"}},
        {"msg_type": 1, "from_user_name": {"str": "user2"}},
    ]
    worker = WeChatMessageWorker(messages, wechat_account=None)

    # Act
    result = worker.has_incoming_message()

    # Assert
    assert result is True


@pytest.mark.unit
def test_has_incoming_message_mixed_types():
    """Test has_incoming_message when there are mixed message types."""
    # Arrange
    messages = [
        {"msg_type": 1, "from_user_name": {"str": "user1"}},
        {"msg_type": 2, "from_user_name": {"str": "user2"}},
    ]
    worker = WeChatMessageWorker(messages, wechat_account=None)

    # Act
    result = worker.has_incoming_message()

    # Assert
    assert result is False


@pytest.mark.unit
def test_group_messages_by_username_multiple_users():
    """Test group_messages_by_username when messages are from multiple users."""
    # Arrange
    messages = [
        {"from_user_name": {"str": "user1"}, "content": {"str": "Message 1"}},
        {"from_user_name": {"str": "user2"}, "content": {"str": "Message 2"}},
        {"from_user_name": {"str": "user1"}, "content": {"str": "Message 3"}},
    ]
    worker = WeChatMessageWorker(messages, wechat_account=None)

    # Act
    grouped_messages = worker.group_messages_by_username()

    # Assert
    assert grouped_messages == {
        "user1": [
            {"from_user_name": {"str": "user1"}, "content": {"str": "Message 1"}},
            {"from_user_name": {"str": "user1"}, "content": {"str": "Message 3"}},
        ],
        "user2": [{"from_user_name": {"str": "user2"}, "content": {"str": "Message 2"}}],
    }


@pytest.mark.unit
def test_is_from_chatroom_true():
    """Test is_from_chatroom returns True for chatroom usernames."""
    # Arrange
    from_wxid = "35019477707@chatroom"

    # Act
    result = WeChatMessageWorker.is_from_chatroom(from_wxid)

    # Assert
    assert result is True


@pytest.mark.unit
def test_is_from_chatroom_false():
    """Test is_from_chatroom returns False for non-chatroom usernames."""
    # Arrange
    from_wxid = "wxid_fdsoz331br5g22"

    # Act
    result = WeChatMessageWorker.is_from_chatroom(from_wxid)

    # Assert
    assert result is False


@pytest.mark.unit
def test_is_mention_true():
    """Test is_mention returns True when content mentions a nickname."""
    # Arrange
    content = "@user1 Hello there!"
    nicknames = ["user1"]

    # Act
    result = WeChatMessageWorker.is_mention(content, nicknames)

    # Assert
    assert result is True


@pytest.mark.unit
def test_is_mention_false():
    """Test is_mention returns False when content does not mention a nickname."""
    # Arrange
    content = "Hello there!"
    nicknames = ["user1"]

    # Act
    result = WeChatMessageWorker.is_mention(content, nicknames)

    # Assert
    assert result is False


@pytest.mark.unit
def test_get_nickname_push_content_not_void():
    """Test get_nickname when push_content contains meaningful content."""
    # Arrange
    push_content = "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて"
    content = "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて"

    # Act
    result = WeChatMessageWorker.get_nickname(push_content, content)

    # Assert
    assert result == "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて"


@pytest.mark.unit
def test_get_nickname_push_content_is_void():
    """Test get_nickname when push_content is void."""
    # Arrange
    push_content = None
    content = "qoitaaxb:\n12个可以吗"

    # Act
    result = WeChatMessageWorker.get_nickname(push_content, content)

    # Assert
    assert result == "Unknown"


@pytest.mark.unit
def test_get_nickname_push_content_does_not_contain_content():
    """Test get_nickname when push_content does not contain content."""
    # Arrange
    push_content = "藤井　広海在群聊中@了你"
    content = "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて"

    # Act
    result = WeChatMessageWorker.get_nickname(push_content, content)

    # Assert
    assert result == "藤井　広海"


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_message_push_content_not_void(mocker):
    """Test process_message when push_content is not void."""
    # Arrange
    message = {
        "msg_id": 1718373982,
        "from_user_name": {"str": "35019477707@chatroom"},
        "to_user_name": {"str": "wxid_flmw60k4a5p12"},
        "content": {"str": "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて"},
        "push_content": "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
    }
    worker = WeChatMessageWorker([message], wechat_account=mocker.Mock())
    account_key = "test_account_key"

    # Mock route_message
    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_message(message, account_key)

    # Assert
    mock_route_message.assert_called_once_with(
        "35019477707@chatroom",
        "wxid_flmw60k4a5p12",
        "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
        "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_message_push_content_is_void(mocker):
    """Test process_message when push_content is void."""
    # Arrange
    message = {
        "msg_id": 871731059,
        "from_user_name": {"str": "51852918759@chatroom"},
        "to_user_name": {"str": "wxid_lw4vw0gu78p22"},
        "content": {"str": "qoitaaxb:\n12个可以吗"},
        "push_content": "",
    }
    worker = WeChatMessageWorker([message], wechat_account=mocker.Mock())
    account_key = "test_account_key"

    # Mock route_message
    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_message(message, account_key)

    # Assert
    mock_route_message.assert_called_once_with(
        "51852918759@chatroom", "wxid_lw4vw0gu78p22", "qoitaaxb:\n12个可以吗", ""
    )


@pytest.mark.unit
@pytest.mark.asyncio
async def test_process_message_push_content_does_not_contain_content(mocker):
    """Test process_message when push_content does not contain content."""
    # Arrange
    message = {
        "msg_id": 1006198057,
        "from_user_name": {"str": "48170981736@chatroom"},
        "to_user_name": {"str": "wxid_flmw60k4a5p12"},
        "content": {"str": "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて"},
        "push_content": "藤井　広海在群聊中@了你",
    }
    worker = WeChatMessageWorker([message], wechat_account=mocker.Mock())
    account_key = "test_account_key"

    # Mock route_message
    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_message(message, account_key)

    # Assert
    mock_route_message.assert_called_once_with(
        "48170981736@chatroom",
        "wxid_flmw60k4a5p12",
        "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて",
        "藤井　広海在群聊中@了你",
    )
