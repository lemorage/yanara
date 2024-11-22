import json
import os
from typing import Any, Dict, List

from rich import print

from yanara.util.reqwest import request


class WeChatAccount:
    current_environment = os.getenv("ENVIRONMENT", "dev")

    def __init__(self, key: str, agent_id: str) -> None:
        self.key = key
        self.agent_id = agent_id

    async def fetch_messages(self) -> List[Dict[str, Any]]:
        """Fetches messages for this WeChat account."""
        url = f"{self.get_service_base_path()}/v1/message/NewSyncHistoryMessage?key={self.key}"
        result = await request(url, {"Scene": 3}, {"method": "post"})
        if result.get("Code") != 200:
            print(f"API call failed with response: '{result}'.")
            return []
        return result.get("Data", {}).get("AddMsgs", []) if result else []

    async def fetch_chatroom_info(self, chatroom_id: str) -> Dict[str, Any]:
        """Fetches chatroom information for the given chatroom ID."""
        url = f"{self.get_service_base_path()}/v1/chatroom/GetChatRoomInfo?key={self.key}"
        result = await request(url, {"ChatRoomWxIdList": [chatroom_id]}, {"method": "post"})
        return result.get("Data", {}) if result else {}

    @classmethod
    def is_production(cls) -> bool:
        """Check if the current environment is production."""
        return cls.current_environment.lower() == "prod"

    def get_service_base_path(self) -> str:
        """Returns the base path for the WeChat agent service depending on the environment."""
        if self.is_production():
            return "http://wechat-agent-service:8011"
        else:
            return "http://127.0.0.1:8011"

    @staticmethod
    def get_wechat_accounts() -> List[Dict[str, Any]]:
        """Retrieve WeChat accounts configuration from the environment."""
        environment = WeChatAccount.current_environment
        config_file = "yanara/configs/wechat_account_mapping.json"

        try:
            with open(config_file, "r") as file:
                data = json.load(file)

            accounts = data.get(environment, [])

            if not accounts:
                print(
                    f"[yellow]Warning: No WeChat accounts found for environment '{environment}' in the configuration file.[/yellow]"
                )

            return accounts
        except FileNotFoundError:
            print(f"[red]Error: The configuration file '{config_file}' was not found.[/red]")
            return []
        except json.JSONDecodeError:
            print(f"[red]Error: Failed to decode the JSON configuration from '{config_file}'.[/red]")
            return []
