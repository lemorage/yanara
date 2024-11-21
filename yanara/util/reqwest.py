from functools import partial
from typing import Any, Dict, Optional

import httpx
from rich import print
from rich.console import Console
from rich.traceback import install

# Install rich traceback for nicer error display in the console
install(show_locals=True)


async def request(
    url: str,
    data: Optional[Dict[str, Any]] = None,
    options: Optional[Dict[str, Any]] = None,
    axios_options: Optional[Dict[str, Any]] = None,
) -> Any:
    """Send an asynchronous HTTP request to a specified URL with optional custom parameters.

    Parameters
    ----------
    - url (str): The URL to send the request to.
    - data (Optional[Dict[str, Any]]): The data to send in the request body (for POST/PUT).
    - options (Optional[Dict[str, Any]]): A dictionary containing request options, including 'method' (GET, POST, PUT).
    - axios_options (Optional[Dict[str, Any]]): Additional axios-like options for the request (e.g., timeout, proxy).

    Returns
    -------
    - Any: The response of the request, assumed to be a JSON object.

    Raises
    ------
    - ValueError: If an unsupported HTTP method is provided.
    - httpx.RequestError: If the request fails (timeout, network issues, etc.).
    """
    options = options or {}
    method = options.get("method", "POST").upper()

    axios_options = axios_options or {}
    default_axios_options = {"timeout": 60, "proxy": None, "httpsAgent": None}
    merged_axios_options = {**default_axios_options, **axios_options}

    # Map HTTP methods to client methods
    method_mapping = {
        "GET": partial(_http_call, http_method="get"),
        "POST": partial(_http_call, http_method="post"),
        "PUT": partial(_http_call, http_method="put"),
    }

    if method not in method_mapping:
        raise ValueError(f"Unsupported method: {method}")

    return await method_mapping[method](url, merged_axios_options, data)


async def _http_call(url: str, axios_options: Dict[str, Any], data: Optional[Dict[str, Any]], http_method: str) -> Any:
    """Make a generalized HTTP call."""
    try:
        client_options = {
            "timeout": axios_options["timeout"],
            "proxy": axios_options["proxy"],
        }

        async with httpx.AsyncClient(**client_options) as client:
            method = getattr(client, http_method)
            response = await method(url, json=data if data else None)
            response.raise_for_status()
            return response.json()

    except httpx.HTTPStatusError as e:
        print(
            f"[bold red]HTTP error {e.response.status_code}[/bold red] occurred while accessing [link={url}]{url}[/link]."
        )
        print(f"[bold yellow]Message:[/bold yellow] {e.response.text}")
        raise
    except httpx.RequestError as e:
        print(f"[bold red]Request error[/bold red] occurred while trying to reach [link={url}]{url}[/link].")
        print(f"[bold yellow]Error details:[/bold yellow] {e}")
        raise
    except Exception as e:
        print(f"[bold red]Unexpected error[/bold red] occurred.")
        print(f"[bold yellow]Error details:[/bold yellow] {e}")
        raise
