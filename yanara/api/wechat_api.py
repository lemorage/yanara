import asyncio
import json
from typing import Any, Dict, List, Optional

import httpx

from yanara.util.reqwest import request


# Helper function to check if there is exactly one type of incoming message
def has_incoming_message(messages: List[Dict[str, Any]]) -> bool:
    """
    Check if there is exactly one type of incoming message (msg_type == 1) and no others.
    """
    return any(item["msg_type"] == 1 for item in messages) and not any(item["msg_type"] != 1 for item in messages)


async def schedule_pulling_wechat_message() -> None:
    try:
        accounts = get_wechat_accounts()

        # Create a list of async tasks for each account
        async def process_account(account: Dict[str, Any]) -> None:
            key = account["key"]
            url = f"{get_wechat_agent_service_base_path()}/v1/message/NewSyncHistoryMessage?key={key}"

            result = await request(url, {"Scene": 3}, {"method": "post"})

            messages = result.get("Data", {}).get("AddMsgs", []) if result else []

            if not messages:
                print("msg: None or empty")
                return

            print("msg: ", messages)

            if has_incoming_message(messages):
                from_usernames = list({item["from_user_name"]["str"] for item in messages})

                # Create tasks to process messages from each 'from_user_name'
                async def process_message(from_username: str) -> None:
                    message = next((item for item in messages if item["from_user_name"]["str"] == from_username), None)

                    if message:
                        print(f"Receiving WeChat message: {message}")

                        from_wxid = message["from_user_name"]["str"]
                        to_wxid = message["to_user_name"]["str"]
                        content = message["content"]["str"]
                        push_content = message.get("push_content")

                        await route_message(from_wxid, to_wxid, content, push_content)

                await asyncio.gather(*(process_message(from_username) for from_username in from_usernames))

        await asyncio.gather(*(process_account(account) for account in accounts))

    except Exception as e:
        print(f"Error: {str(e)}")


# Mock helper functions to simulate the behavior
def get_wechat_accounts() -> List[Dict[str, Any]]:
    return [
        {
            "key": "",
            "wxid": "",
            "nicknames": [""],
            "identifier": "",
        },
    ]


def get_wechat_agent_service_base_path() -> str:
    return "http://127.0.0.1:8011"


async def route_message(from_wxid: str, to_wxid: str, content: str, push_content: Optional[str]) -> None:
    print(f"Routing message from {from_wxid} to {to_wxid} with content: {content}, push content: {push_content}")


async def monitor_wechat_messages():
    while True:
        await schedule_pulling_wechat_message()
        await asyncio.sleep(5)


if __name__ == "__main__":
    asyncio.run(monitor_wechat_messages())
