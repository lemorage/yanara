import asyncio
from datetime import datetime
import json
import os
import signal
from typing import Any, Dict, List, Optional

import httpx
from rich import print

from yanara.api.wechat_api.wechat_account import WeChatAccount
from yanara.util.decorators import entry
from yanara.util.reqwest import request


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


# Main WeChatService class that manages the system
class WeChatService:
    def __init__(self):
        self.accounts = [WeChatAccount(key=account["key"]) for account in WeChatAccount.get_wechat_accounts()]

    async def schedule_pulling_messages(self) -> None:
        """Schedule and process messages for all WeChat accounts."""
        tasks = [self.process_account(account) for account in self.accounts]
        await asyncio.gather(*tasks)

    async def process_account(self, account: WeChatAccount) -> None:
        """Process messages for a single WeChat account."""
        messages = await account.fetch_messages()
        current_time = str(datetime.now())[:-7]
        if not messages:
            print(f"[{current_time}]: Currently no messages.")
            return

        print(f"[{current_time}]: ", messages)
        processor = WeChatMessageProcessor(messages)

        if processor.has_incoming_message():
            await processor.process_messages(account.key)


# Monitoring loop to keep pulling messages until the stop signal is received
async def monitor_wechat_messages(stop_flag: asyncio.Event) -> None:
    """Monitor and process WeChat messages until stop flag is set."""
    print("Monitoring WeChat messages...")
    service = WeChatService()
    while not stop_flag.is_set():
        await service.schedule_pulling_messages()
        await asyncio.sleep(5)
    print("Monitoring stopped.")


# Stop signal handler to stop the loop
def stop_loop(signal_received, frame, stop_flag: asyncio.Event) -> None:
    """Handles the shutdown signal and sets the stop flag."""
    stop_flag.set()
    print("Shutdown signal received. Stopping...")


@entry
def main():
    stop_flag = asyncio.Event()

    # Register the signal handler
    signal.signal(signal.SIGINT, lambda s, f: stop_loop(s, f, stop_flag))
    signal.signal(signal.SIGTERM, lambda s, f: stop_loop(s, f, stop_flag))

    asyncio.run(monitor_wechat_messages(stop_flag))
