import asyncio
from datetime import datetime
import signal

from rich import print

from yanara.api.wechat_api.wechat_account import WeChatAccount
from yanara.api.wechat_api.wechat_message_processor import WeChatMessageProcessor


class WeChatService:
    def __init__(self, agent_id: str) -> None:
        self.accounts = [WeChatAccount(account["key"], agent_id) for account in WeChatAccount.get_wechat_accounts()]

    async def schedule_pulling_messages(self) -> None:
        """Schedule and process messages for all WeChat accounts."""
        tasks = [self.process_account(account) for account in self.accounts]
        await asyncio.gather(*tasks)

    async def process_account(self, account: WeChatAccount) -> None:
        """Process messages for a single WeChat account."""
        messages = await account.fetch_messages()
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        if not messages:
            return

        # Filter messages by type
        filtered_messages = [msg for msg in messages if msg["msg_type"] < 48]

        if filtered_messages:
            print(f"[{current_time}]: {filtered_messages}")

            processor = WeChatMessageProcessor(filtered_messages, account)

            if processor.has_incoming_message():
                await processor.process_messages(account.key)
