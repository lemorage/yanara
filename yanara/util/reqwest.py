from typing import Any, Dict, Optional

import httpx


async def request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    axios_options: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Send an asynchronous HTTP request to a specified URL with optional custom parameters.

    Parameters:
    - url (str): The URL to send the request to.
    - data (Optional[Dict[str, Any]]): The data to send in the request body (for POST/PUT).
    - options (Optional[Dict[str, Any]]): A dictionary containing request options, including 'method' (GET, POST, PUT).
    - axios_options (Optional[Dict[str, Any]]): Additional axios-like options for the request (e.g., timeout, proxy).

    Returns:
    - Any: The response of the request, assumed to be a JSON object.

    Raises:
    - ValueError: If an unsupported HTTP method is provided.
    - httpx.RequestError: If the request fails (timeout, network issues, etc.).
    """

    options = options or {}
    method = options.get("method", "POST").upper()

    axios_options = axios_options or {}
    default_axios_options = {"timeout": 60, "proxy": None, "httpsAgent": None}
    merged_axios_options = {**default_axios_options, **axios_options}

    # Prepare request parameters
    params = {"url": url, "timeout": merged_axios_options["timeout"], "proxies": merged_axios_options["proxy"]}

    # Handle GET request
    if method == "GET":
        return await _get_request(params)

    # Handle POST or PUT request
    elif method in ["POST", "PUT"]:
        return await _post_or_put_request(method, params, data)

    raise ValueError(f"Unsupported method: {method}")


async def _get_request(params: Dict[str, Any]) -> Any:
    """
    Perform an asynchronous GET request with the given parameters.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(params["url"], timeout=params["timeout"], proxies=params["proxies"])
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise ValueError(f"GET request failed: {e}")


async def _post_or_put_request(method: str, params: Dict[str, Any], data: Optional[Dict[str, Any]]) -> Any:
    """
    Perform an asynchronous POST or PUT request with the given parameters.
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method, params["url"], json=data, timeout=params["timeout"], proxies=params["proxies"]
            )
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as e:
        raise ValueError(f"{method} request failed: {e}")
