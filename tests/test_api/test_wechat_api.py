import asyncio
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from yanara.api.wechat_api.wechat_account import WeChatAccount
from yanara.api.wechat_api.wechat_message_manager import WeChatMessageManager
from yanara.api.wechat_api.wechat_message_worker import WeChatMessageWorker

################################################
#                                              #
#  WeChatMessageWorker class tests (yanara)    #
#                                              #
################################################


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
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "from_wxid, to_wxid, content, push_content, account_data, expected_nickname, should_call_chat",
    [
        # Case 1: Account found, valid push_content
        (
            "user1@chatroom",
            "wxid_user1",
            "nickname_id: Hello, how are you?",
            "nickname: Hello, how are you?",
            {"identifier": "agent_123"},
            "nickname",
            True,
        ),
        # Case 2: Account not found
        (
            "user2@chatroom",
            "wxid_user2",
            "nickname_id: Test message",
            None,
            None,
            "Unknown",
            False,
        ),
        # Case 3: Push content is void
        (
            "user3@chatroom",
            "wxid_user3",
            "nickname_id: Test message",
            None,
            {"identifier": "agent_456"},
            "Unknown",
            True,
        ),
    ],
)
async def test_route_message(
    mocker,
    from_wxid,
    to_wxid,
    content,
    push_content,
    account_data,
    expected_nickname,
    should_call_chat,
):
    """Test the route_message method for different scenarios."""
    # Arrange
    wechat_account_mock = Mock()
    wechat_account_mock.get_account_by_wxid = Mock(return_value=account_data)

    worker = WeChatMessageWorker([], wechat_account=wechat_account_mock)

    mock_chat = mocker.patch.object(worker, "chat", return_value=None)

    # Act
    await worker.route_message(from_wxid, to_wxid, content, push_content)

    # Assert
    wechat_account_mock.get_account_by_wxid.assert_called_once_with(to_wxid)

    if account_data:
        mock_chat.assert_called_once_with(account_data["identifier"], from_wxid, expected_nickname, content)
    else:
        mock_chat.assert_not_called()


@pytest.mark.unit
@pytest.mark.parametrize(
    "from_wxid, expected",
    [
        (
            "35019477707@chatroom",
            True,
        ),
        (
            "wxid_fdsoz331br5g22",
            False,
        ),
    ],
)
def test_is_from_chatroom(from_wxid, expected):
    """Test is_from_chatroom for True and False cases."""
    # Act
    result = WeChatMessageWorker.is_from_chatroom(from_wxid)

    # Assert
    assert result is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "content, nicknames, expected",
    [
        (
            "@user1 Hello there!",
            ["user1"],
            True,
        ),
        (
            "Hello there!",
            ["user1"],
            False,
        ),
    ],
)
def test_is_mention_true(content, nicknames, expected):
    """Test is_mention for True and False cases"""
    # Act
    result = WeChatMessageWorker.is_mention(content, nicknames)

    # Assert
    assert result is expected


@pytest.mark.unit
@pytest.mark.parametrize(
    "push_content, content, expected",
    [
        # Case 1: push_content is not void
        (
            "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
            "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
            "miao.",
        ),
        # Case 2: push_content is void
        (
            None,
            "qoitaaxb:\n12个可以吗",
            "Unknown",
        ),
        # Case 3: push_content does not contain content
        (
            "藤井　広海在群聊中@了你",
            "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて",
            "藤井　広海",
        ),
    ],
)
def test_get_nickname(push_content, content, expected):
    """Test get_nickname for different message scenarios."""
    # Act
    result = WeChatMessageWorker.get_nickname(push_content, content)

    # Assert
    assert result == expected


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "message, account_key, expected_from_user, expected_to_user, expected_content, expected_push_content",
    [
        # Case 1: push_content is not void
        (
            {
                "msg_id": 1718373982,
                "from_user_name": {"str": "35019477707@chatroom"},
                "to_user_name": {"str": "wxid_flmw60k4a5p12"},
                "content": {"str": "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて"},
                "push_content": "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
            },
            "test_account_key",
            "35019477707@chatroom",
            "wxid_flmw60k4a5p12",
            "wxid_fdsoz331br5g22:\n@小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
            "miao. : @小境子在日本 来年1月4日宿泊者2名、空室と料金教えて",
        ),
        # Case 2: push_content is void
        (
            {
                "msg_id": 871731059,
                "from_user_name": {"str": "51852918759@chatroom"},
                "to_user_name": {"str": "wxid_lw4vw0gu78p22"},
                "content": {"str": "qoitaaxb:\n12个可以吗"},
                "push_content": "",
            },
            "test_account_key",
            "51852918759@chatroom",
            "wxid_lw4vw0gu78p22",
            "qoitaaxb:\n12个可以吗",
            "",
        ),
        # Case 3: push_content does not contain content
        (
            {
                "msg_id": 1006198057,
                "from_user_name": {"str": "48170981736@chatroom"},
                "to_user_name": {"str": "wxid_flmw60k4a5p12"},
                "content": {"str": "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて"},
                "push_content": "藤井　広海在群聊中@了你",
            },
            "test_account_key",
            "48170981736@chatroom",
            "wxid_flmw60k4a5p12",
            "wxid_4j07o2334ksk12:\n@小境子在日本 1月4日宿泊者2名、空室と料金教えて",
            "藤井　広海在群聊中@了你",
        ),
    ],
)
async def test_process_message(
    mocker,
    message,
    account_key,
    expected_from_user,
    expected_to_user,
    expected_content,
    expected_push_content,
):
    """Parametrized test for process_message with various push_content scenarios."""
    # Arrange
    worker = WeChatMessageWorker([message], wechat_account=mocker.Mock())
    mock_route_message = mocker.patch.object(worker, "route_message", return_value=asyncio.Future())
    mock_route_message.return_value.set_result(None)

    # Act
    await worker.process_message(message, account_key)

    # Assert
    mock_route_message.assert_called_once_with(
        expected_from_user, expected_to_user, expected_content, expected_push_content
    )


################################################
#                                              #
#  WeChatMessageManager class tests (yanara)   #
#                                              #
################################################


@pytest.mark.unit
@pytest.mark.asyncio
async def test_schedule_pulling_messages(mocker):
    """Test the schedule_pulling_messages method."""
    # Arrange
    mock_account = Mock()
    mock_account.fetch_messages = Mock(return_value=[])
    mock_accounts = [mock_account, mock_account]

    mocker.patch(
        "yanara.api.wechat_api.wechat_account.WeChatAccount.get_wechat_accounts",
        return_value=[{"key": "account1"}, {"key": "account2"}],
    )
    manager = WeChatMessageManager(agent_id="agent_123")
    manager.accounts = mock_accounts

    mock_process_account = mocker.patch.object(manager, "process_account", return_value=asyncio.Future())
    mock_process_account.return_value.set_result(None)

    # Act
    await manager.schedule_pulling_messages()

    # Assert
    assert mock_process_account.call_count == len(manager.accounts)
    mock_process_account.assert_any_call(mock_account)


@pytest.mark.asyncio
@pytest.mark.integration
@pytest.mark.parametrize(
    "messages, expected_filtered_messages, should_process_messages",
    [
        # Case 1: All valid messages with msg_type 1, should process
        (
            [
                {
                    "msg_type": 1,
                    "content": {"str": "Message 1"},
                    "from_user_name": {"str": "user123"},
                    "to_user_name": {"str": "agent123"},
                    "push_content": "nicky : Hello",
                },
                {
                    "msg_type": 1,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user456"},
                    "to_user_name": {"str": "agent456"},
                    "push_content": "micky : Howdy",
                },
            ],
            [
                {
                    "msg_type": 1,
                    "content": {"str": "Message 1"},
                    "from_user_name": {"str": "user123"},
                    "to_user_name": {"str": "agent123"},
                    "push_content": "nicky : Hello",
                },
                {
                    "msg_type": 1,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user456"},
                    "to_user_name": {"str": "agent456"},
                    "push_content": "micky : Howdy",
                },
            ],
            True,
        ),
        # Case 2: Some messages with non-msg_type 1, should not process
        (
            [
                {
                    "msg_type": 1,
                    "content": {"str": "Message 1"},
                    "from_user_name": {"str": "user1"},
                    "to_user_name": {"str": "user2"},
                    "push_content": "nickname : Hello",
                },
                {
                    "msg_type": 47,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user2"},
                    "to_user_name": {"str": "user1"},
                    "push_content": None,
                },
                {
                    "msg_type": 49,
                    "content": {"str": "Message 3"},
                    "from_user_name": {"str": "user3"},
                    "to_user_name": {"str": "user4"},
                    "push_content": None,
                },
            ],
            [
                {
                    "msg_type": 1,
                    "content": {"str": "Message 1"},
                    "from_user_name": {"str": "user1"},
                    "to_user_name": {"str": "user2"},
                    "push_content": "nickname : Hello",
                },
                {
                    "msg_type": 47,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user2"},
                    "to_user_name": {"str": "user1"},
                    "push_content": None,
                },
            ],
            False,
        ),
        # Case 3: No valid messages (no msg_type 1), should not process
        (
            [
                {
                    "msg_type": 47,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user1"},
                    "to_user_name": {"str": "user2"},
                    "push_content": None,
                },
                {
                    "msg_type": 49,
                    "content": {"str": "Message 3"},
                    "from_user_name": {"str": "user3"},
                    "to_user_name": {"str": "user4"},
                    "push_content": None,
                },
            ],
            [
                {
                    "msg_type": 47,
                    "content": {"str": "Message 2"},
                    "from_user_name": {"str": "user1"},
                    "to_user_name": {"str": "user2"},
                    "push_content": None,
                }
            ],
            False,
        ),
        # Case 4: Empty message list, should not process
        ([], [], False),
    ],
)
async def test_process_account(mocker, messages, expected_filtered_messages, should_process_messages):
    """Test the process_account method of WeChatMessageManager."""

    # Arrange
    account_mock = Mock()
    account_mock.fetch_messages = AsyncMock(return_value=messages)
    account_mock.key = "f93740hd921038"

    mock_account = {"identifier": "agent_123"}
    account_mock.get_account_by_wxid = Mock(return_value=mock_account)

    worker_mock = Mock()
    worker_mock.has_incoming_message = Mock(return_value=True if should_process_messages else False)
    worker_mock.process_messages = AsyncMock()

    mock_wechat_account = Mock()
    mock_wechat_account.agent_id = "agent_123"

    worker_mock.wechat_account = mock_wechat_account

    mocker.patch("yanara.api.wechat_api.wechat_message_manager.WeChatMessageWorker", return_value=worker_mock)

    manager = WeChatMessageManager(agent_id="agent_123")

    # Act
    await manager.process_account(account_mock)

    # Assert: Check if messages were filtered correctly
    filtered_messages = [msg for msg in messages if msg["msg_type"] < 48]
    assert filtered_messages == expected_filtered_messages

    if should_process_messages and messages:
        worker_mock.has_incoming_message.assert_called_once()
        worker_mock.process_messages.assert_awaited_once_with(account_mock.key)
    elif messages:
        worker_mock.has_incoming_message.assert_called_once()
        worker_mock.process_messages.assert_not_called()
    else:
        worker_mock.has_incoming_message.assert_not_called()
        worker_mock.process_messages.assert_not_called()


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "messages, expected_result",
    [
        # Case 1: Mock response from API, should return messages list
        (
            {"Code": 200, "Data": {"AddMsgs": [{"msg_type": 1, "content": "Hello"}]}},
            [{"msg_type": 1, "content": "Hello"}],
        ),
        # Case 2: Empty result from API
        ({"Data": {}}, []),
        # Case 3: API returns no result
        (None, []),
    ],
)
async def test_fetch_messages(mocker, messages, expected_result):
    """Test fetch_messages for WeChatAccount."""

    # Arrange
    account_mock = Mock()
    account_mock.key = "test_key"
    mocker.patch("yanara.api.wechat_api.wechat_account.request", return_value=messages)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = await account.fetch_messages()

    # Assert
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "chatroom_id, mock_response, expected_result",
    [
        # Case 1: Valid response from the API
        (
            "chatroom_1",
            {"Data": {"id": "chatroom_1", "name": "Test Chatroom"}},
            {"id": "chatroom_1", "name": "Test Chatroom"},
        ),
        # Case 2: API returns empty data
        ("chatroom_2", {"Data": {}}, {}),
        # Case 3: API returns no response
        ("chatroom_3", None, {}),
    ],
)
async def test_fetch_chatroom_info(mocker, chatroom_id, mock_response, expected_result):
    """Test fetch_chatroom_info for WeChatAccount."""

    # Arrange
    account_mock = Mock()
    account_mock.key = "test_key"
    mocker.patch("yanara.api.wechat_api.wechat_account.request", return_value=mock_response)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = await account.fetch_chatroom_info(chatroom_id)

    # Assert
    assert result == expected_result


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, content, mock_response",
    [
        ("user_1", "Hello!", {"status": "success"}),
        ("user_2", "Goodbye!", {"status": "success"}),
        ("user_3", "Hi!", {"status": "failure"}),
    ],
)
async def test_send_wechat_message(mocker, user_id, content, mock_response):
    """Test send_wechat_message for WeChatAccount."""

    # Arrange
    account_mock = Mock()
    account_mock.key = "test_key"
    mocker.patch("yanara.api.wechat_api.wechat_account.request", return_value=mock_response)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = await account.send_wechat_message(user_id, content)

    # Assert
    assert result == mock_response


@pytest.mark.unit
@pytest.mark.asyncio
@pytest.mark.parametrize(
    "user_id, image, mock_response",
    [
        ("user_1", "image_url_1", {"status": "success"}),
        ("user_2", "image_url_2", {"status": "success"}),
        ("user_3", "image_url_3", {"status": "failure"}),
    ],
)
async def test_send_wechat_image_message(mocker, user_id, image, mock_response):
    """Test send_wechat_image_message for WeChatAccount."""

    # Arrange
    account_mock = Mock()
    account_mock.key = "test_key"
    mocker.patch("yanara.api.wechat_api.wechat_account.request", return_value=mock_response)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = await account.send_wechat_image_message(user_id, image)

    # Assert
    assert result == mock_response


@pytest.mark.unit
@pytest.mark.parametrize(
    "wxid, expected_account",
    [
        # Case 1: Account found
        ("wxid_1", {"wxid": "wxid_1", "key": "test_key", "agent_id": "test_agent"}),
        # Case 2: Account not found
        ("wxid_999", None),
    ],
)
def test_get_account_by_wxid(mocker, wxid, expected_account):
    """Test get_account_by_wxid for WeChatAccount."""

    # Arrange
    mock_accounts = [
        {"wxid": "wxid_1", "key": "test_key", "agent_id": "test_agent"},
        {"wxid": "wxid_2", "key": "test_key_2", "agent_id": "test_agent_2"},
    ]
    mocker.patch.object(WeChatAccount, "get_wechat_accounts", return_value=mock_accounts)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = account.get_account_by_wxid(wxid)

    # Assert
    assert result == expected_account


@pytest.mark.unit
@pytest.mark.parametrize(
    "environment, expected_path",
    [
        # Case 1: Environment is dev (default)
        ("dev", "http://127.0.0.1:8011"),
        # Case 2: Environment is prod
        ("prod", "http://wechat-agent-service:8011"),
    ],
)
def test_get_service_base_path(monkeypatch, environment, expected_path):
    """Test get_service_base_path for WeChatAccount."""

    # Arrange: Temporarily set the class variable `current_environment`
    monkeypatch.setattr(WeChatAccount, "current_environment", environment)

    account = WeChatAccount(key="test_key", agent_id="test_agent")

    # Act
    result = account.get_service_base_path()

    # Assert
    assert result == expected_path


@pytest.mark.unit
@pytest.mark.parametrize(
    "file_content, expected_accounts",
    [
        # Case 1: Valid file content
        (
            '{"dev": [{"wxid": "wxid_1", "key": "test_key", "agent_id": "test_agent"}]}',
            [{"wxid": "wxid_1", "key": "test_key", "agent_id": "test_agent"}],
        ),
        # Case 2: Invalid file content
        ("invalid_json", []),
        # Case 3: File not found
        (None, []),
    ],
)
def test_get_wechat_accounts(mocker, file_content, expected_accounts):
    """Test get_wechat_accounts for WeChatAccount."""

    # Arrange
    config_file = "yanara/configs/wechat_account_mapping.json"
    if file_content:
        mocker.patch("builtins.open", mocker.mock_open(read_data=file_content))
    else:
        mocker.patch("builtins.open", mocker.MagicMock(side_effect=FileNotFoundError))

    # Act
    result = WeChatAccount.get_wechat_accounts()

    # Assert
    assert result == expected_accounts
