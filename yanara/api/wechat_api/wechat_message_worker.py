import base64
from collections import defaultdict
import os
from typing import Any, Dict, List, Optional

from rich import print

from yanara.api.wechat_api.wechat_account import WeChatAccount
from yanara.globals import client
from yanara.helpers.letta_message_helper import (
    extract_file_path_from_function_return,
    extract_message_from_function_call,
)


class WeChatMessageWorker:
    def __init__(self, messages: List[Dict[str, Any]], wechat_account: WeChatAccount) -> None:
        """Initialize with the list of messages and a WeChatAccount instance."""
        self.messages = messages
        self.wechat_account = wechat_account

    def has_incoming_message(self) -> bool:
        """Returns True if there is exactly one incoming message type (msg_type == 1)."""
        return any(item["msg_type"] == 1 for item in self.messages) and not any(
            item["msg_type"] != 1 for item in self.messages
        )

    def extract_usernames(self) -> List[str]:
        """Extract distinct 'from_user_name' from messages."""
        return list({item["from_user_name"]["str"] for item in self.messages})

    async def process_messages(self, account_key: str) -> None:
        """
        Process all messages for each username.
        """
        grouped_messages = self.group_messages_by_username()
        for username, user_messages in grouped_messages.items():
            for message in user_messages:
                await self.process_message(message, account_key)

    def group_messages_by_username(self) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group all messages by their 'from_user_name'.
        Returns a dictionary where keys are usernames, and values are lists of messages.
        """
        grouped_messages = defaultdict(list)
        for message in self.messages:
            username = message["from_user_name"]["str"]
            grouped_messages[username].append(message)
        return grouped_messages

    async def process_message(self, message: Dict[str, Any], account_key: str) -> None:
        """
        Process and route a single message.

        Handles messages with an optional `push_content` field:
        - If `push_content` is None, the message is ignored.
        - If `push_content` is not None, it can take two forms:
            1. "nickname : content"
            2. "nickname 在群聊中@了你"
        """
        from_wxid = message["from_user_name"]["str"]
        to_wxid = message["to_user_name"]["str"]
        content = message["content"]["str"]
        push_content = message.get("push_content")
        await self.route_message(from_wxid, to_wxid, content, push_content)

    async def route_message(self, from_wxid: str, to_wxid: str, content: str, push_content: Optional[str]) -> None:
        """Handles message routing by printing the message details."""
        print(f"Routing message from {from_wxid} to {to_wxid} with content: {content}, push content: {push_content}")

        account = self.wechat_account.get_account_by_wxid(to_wxid)
        if not account:
            print(f"Account not found for wxid: {to_wxid}")
            return

        agent_id = account["identifier"]
        nickname = WeChatMessageWorker.get_nickname(push_content, content)

        await self.chat(agent_id, from_wxid, nickname, content)

    async def chat(self, agent_id: str, user_id: str, nickname: str, content: str) -> None:
        """Chat with the given agent in the specified language."""
        print(f"Agent {agent_id} is chatting with nickname {nickname}")
        if not WeChatMessageWorker.is_from_chatroom(user_id):
            response = client.send_message(agent_id=self.wechat_account.agent_id, role="user", message=content)
            print("debug response:", response)
            result = extract_file_path_from_function_return(response.messages)
            if result[0]:
                file_path = result[1]
                if os.path.isfile(file_path):
                    try:
                        # Read the image from the file path
                        with open(file_path, "rb") as img_file:
                            img_data = img_file.read()
                            # Encode the image data to base64
                            img_base64 = base64.b64encode(img_data).decode("utf-8")

                        # Send the image as a base64 string
                        await self.wechat_account.send_wechat_image_message(user_id, img_base64)
                    finally:
                        # Delete the temporary file after use
                        if os.path.isfile(file_path):  # Double check if the file still exists
                            os.remove(file_path)
                            print(f"Deleted temporary image file at {file_path}")
                else:
                    print(f"Error: File not found at {file_path}")
            else:
                x = await self.wechat_account.send_wechat_message(
                    user_id, extract_message_from_function_call(response.messages)
                )

        # TODO:
        #     return
        # else:
        #     if is_mention(content, [nickname]):
        #         print(f"Mentioning {nickname} in the content: {content}")

    @staticmethod
    def is_from_chatroom(from_wxid: str) -> bool:
        """Checks if the message is from a chatroom."""
        return "@chatroom" in from_wxid

    @staticmethod
    def is_mention(content: str, nicknames: List[str]) -> bool:
        """Checks if the content mentions any of the given nicknames."""
        return any(nickname in content for nickname in nicknames)

    @staticmethod
    def get_nickname(push_content: str, content: str) -> str:
        """Extracts the nickname from the push content."""
        if push_content is None:
            return "Unknown"
        if ":" in push_content and ":" in content:
            return push_content.split(":", 1)[0].strip()
        return push_content.replace("在群聊中@了你", "").strip()
