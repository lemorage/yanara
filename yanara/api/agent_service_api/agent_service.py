import os
from typing import Any

from yanara.util.reqwest import request


def get_agent_service_base_path() -> str:
    """Determine the base path for the agent service based on the environment."""
    if os.getenv("ENVIRONMENT") == "prod":
        return "http://agent-service:4050"
    else:
        return "http://127.0.0.1:4050"


async def request_send_message(data: dict[str, Any]) -> Any:
    """Send a message to the integration/send endpoint of the agent service.

    Parameters
    ----------
    - data (dict): The data payload to send to the endpoint.

    Returns
    -------
    - Any: The JSON response from the server.
    """
    url = f"{get_agent_service_base_path()}/integration/send"
    options = {"method": "POST"}
    axios_options = {"httpsAgent": None, "proxy": False}

    return await request(url, data=data, options=options, axios_options=axios_options)
