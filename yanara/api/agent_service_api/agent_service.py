import os
from typing import Any

from yanara.util.reqwest import request


class AgentServiceClient:
    """
    Client for interacting with the Agent Service.

    This class provides an interface to send messages using a specific WeCom account
    via the `integration/send` endpoint. The client is initialized with a WeCom account
    identifier, which determines which bot account is used for sending messages.

    Attributes
    ----------
    wecom_id : str
        The WeCom bot ID corresponding to the specified account name.

    Methods
    -------
    get_agent_service_base_path() -> str
        Determines the base URL for the agent service depending on the environment.

    send_wecom_message(chat_id: str, mention_id: Optional[str], content: str) -> Any
        Sends a message to a specified chat with the provided content and mention ID (optional).
    """

    # Mapping of WeCom account names to bot IDs
    _wecom_bot_mappings = {
        "智能助手": "1688856251401888",
        "六一三AI替身": "1688851120680020",
        "外滩34号": "1688858397487548",
    }

    def __init__(self, wecom: str) -> None:
        """
        Initialize the client with a WeCom account.

        Parameters
        ----------
        wecom : str
            The name of the WeCom account to use for sending messages.
            Must match one of the keys in the `_wecom_bot_mappings`.
        """
        self.wecom_id = AgentServiceClient._wecom_bot_mappings.get(wecom, "")
        if not self.wecom_id:
            raise ValueError(f"Invalid WeCom account: {wecom}")

    @staticmethod
    def get_agent_service_base_path() -> str:
        """
        Determine the base path for the agent service based on the environment.

        Returns
        -------
        str
            The base URL of the agent service. The URL varies depending on whether
            the environment is production or development.
        """
        if os.getenv("ENVIRONMENT") == "production":
            return "http://agent-service:4050"
        else:
            return "http://127.0.0.1:4050"

    async def send_wecom_message(self, chat_id: str, content: str, mention_id: str | None = "") -> Any:
        """Send a message from the WeCom accounts through the `integration/send` endpoint.

        Parameters
        ----------
        chat_id : str
            The wechat user for the chat to send the message to.

        content : str
            The content of the message to send.

        mention_id : Optional[str], optional
            The WeChat account IDs to mention in the message. If not provided,
            no user is mentioned. Default is an empty string (no mention).
        """
        if not chat_id or not content:
            raise ValueError("Both chat_id and content must be provided.")

        data = {
            "message": {
                "chat_id": chat_id,
                "mention_id": mention_id,
                "bot_wxid": self.wecom_id,
                "replyContent": content,
            }
        }

        url = f"{self.get_agent_service_base_path()}/integration/send"
        options = {"method": "POST"}
        axios_options = {"httpsAgent": None, "proxy": False}

        return await request(url, data=data, options=options, axios_options=axios_options)
