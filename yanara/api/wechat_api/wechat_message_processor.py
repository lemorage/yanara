from typing import Any, Dict, List, Optional

from rich import print


class WeChatMessageProcessor:
    def __init__(self, messages: List[Dict[str, Any]]) -> None:
        """Initialize with the list of messages."""
        self.messages = messages

    def has_incoming_message(self) -> bool:
        """Returns True if there is exactly one incoming message type (msg_type == 1)."""
        return any(item["msg_type"] == 1 for item in self.messages) and not any(
            item["msg_type"] != 1 for item in self.messages
        )

    def extract_usernames(self) -> List[str]:
        """Extract distinct 'from_user_name' from messages."""
        return list({item["from_user_name"]["str"] for item in self.messages})

    async def process_messages(self, account_key: str) -> None:
        """Process each message based on the username."""
        usernames = self.extract_usernames()
        for from_username in usernames:
            message = self._get_message_by_username(from_username)
            if message:
                await self.process_message(message, account_key)

    async def process_message(self, message: Dict[str, Any], account_key: str) -> None:
        """Process a single message and route it."""
        from_wxid = message["from_user_name"]["str"]
        to_wxid = message["to_user_name"]["str"]
        content = message["content"]["str"]
        push_content = message.get("push_content")
        await self.route_message(from_wxid, to_wxid, content, push_content)

    async def route_message(self, from_wxid: str, to_wxid: str, content: str, push_content: Optional[str]) -> None:
        """Handles message routing by printing the message details."""
        print(f"Routing message from {from_wxid} to {to_wxid} with content: {content}, push content: {push_content}")

    def _get_message_by_username(self, username: str) -> Optional[Dict[str, Any]]:
        """Helper method to get a message by the 'from_user_name'."""
        return next((item for item in self.messages if item["from_user_name"]["str"] == username), None)

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
        if content not in push_content:
            return push_content.replace("在群聊中@了你", "").strip()
        return push_content.replace(content, "").strip().rstrip().strip()
