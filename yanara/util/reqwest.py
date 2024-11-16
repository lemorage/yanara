from typing import Any, Dict, Optional

import requests


def request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    axios_options: Optional[Dict[str, Any]] = None,
) -> Any:
    """
    Send an HTTP request to a specified URL with optional custom parameters.

    Parameters:
    - url (str): The URL to send the request to.
    - data (Optional[Dict[str, Any]]): The data to send in the request body (for POST/PUT).
    - options (Optional[Dict[str, Any]]): A dictionary containing request options, including 'method' (GET, POST, PUT).
    - axios_options (Optional[Dict[str, Any]]): Additional axios-like options for the request (e.g., timeout, proxy).

    Returns:
    - Any: The response of the request, assumed to be a JSON object.

    Raises:
    - ValueError: If an unsupported HTTP method is provided.
    - requests.RequestException: If the request fails (timeout, network issues, etc.).
    """
    options = options or {}
    axios_options = axios_options or {}

    default_axios_options = {"timeout": 60, "proxy": None, "httpsAgent": None}
    merged_axios_options = {**default_axios_options, **axios_options}

    # Get the method (GET, POST, PUT), default to POST
    method = options.get("method", "POST").upper()

    request_params = {"url": url, "timeout": merged_axios_options["timeout"], "proxies": merged_axios_options["proxy"]}

    if method == "GET":
        return _get_request(request_params)
    elif method in ["POST", "PUT"]:
        return _post_or_put_request(method, request_params, data)
    raise ValueError(f"Unsupported method: {method}")


def _get_request(params: Dict[str, Any]) -> Any:
    """
    Perform a GET request with the given parameters.

    Parameters:
    - params (Dict[str, Any]): A dictionary containing URL, timeout, and proxy settings.

    Returns:
    - Any: The response of the GET request, assumed to be a JSON object.
    """
    try:
        response = requests.get(params["url"], timeout=params["timeout"], proxies=params["proxies"])
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ValueError(f"GET request failed: {e}")


def _post_or_put_request(method: str, params: Dict[str, Any], data: Optional[Dict[str, Any]]) -> Any:
    """
    Perform a POST or PUT request with the given parameters.

    Parameters:
    - method (str): The HTTP method ('POST' or 'PUT').
    - params (Dict[str, Any]): A dictionary containing URL, timeout, and proxy settings.
    - data (Optional[Dict[str, Any]]): The data to send in the request body.

    Returns:
    - Any: The response of the POST/PUT request, assumed to be a JSON object.
    """
    try:
        response = requests.request(
            method, params["url"], json=data, timeout=params["timeout"], proxies=params["proxies"]
        )
        response.raise_for_status()
        return response.json()
    except requests.RequestException as e:
        raise ValueError(f"{method} request failed: {e}")
