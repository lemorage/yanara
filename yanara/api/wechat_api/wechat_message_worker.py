from collections import defaultdict
from typing import Any, Dict, List, Optional

from letta.client.client import LocalClient
from rich import print

from yanara.api.wechat_api.wechat_account import WeChatAccount
from yanara.util.detect_lang import LANGUAGES, detect_from_text


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
        """Process a single message and route it."""
        from_wxid = message["from_user_name"]["str"]
        to_wxid = message["to_user_name"]["str"]
        content = message["content"]["str"]
        push_content = message.get("push_content")
        await self.route_message(from_wxid, to_wxid, content, push_content)

    async def route_message(self, from_wxid: str, to_wxid: str, content: str, push_content: Optional[str]) -> None:
        """Handles message routing by printing the message details."""
        print(f"Routing message from {from_wxid} to {to_wxid} with content: {content}, push content: {push_content}")

        account = await self.wechat_account.get_account_by_wxid(to_wxid)
        if not account:
            print(f"Account not found for wxid: {to_wxid}")
            return

        agent_id = account["identifier"]
        lang = detect_from_text(content, LANGUAGES, confidence_threshold=0.7)
        nickname = WeChatMessageWorker.get_nickname(push_content, content)

        await self.chat(from_wxid, agent_id, lang, nickname, content)

    async def chat(self, user_id: str, agent_id: str, lang: str, nickname: str, content: str) -> None:
        """Chat with the given agent in the specified language."""
        print(f"Chatting with agent {agent_id} in language {lang} with nickname {nickname}")
        if not WeChatMessageWorker.is_from_chatroom(agent_id):
            response = client.send_message(agent_id=agent_id, role="user", message=content)
            await self.wechat_account.send_wechat_message(user_id, self.messages, str(response))
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
        # TODO: can get nickname also when not mentioning -> push_content.split(":", 1)[0].strip()
        # TODO: multi-language replacement
        if content not in push_content:
            return push_content.replace("在群聊中@了你", "").strip()
        return push_content.replace(content, "").strip().rstrip().strip()
