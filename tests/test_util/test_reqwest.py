from unittest.mock import AsyncMock
import warnings

import httpx
import pytest

from yanara.util.reqwest import request


@pytest.fixture(autouse=True)
def suppress_warnings():
    """
    A pytest fixture that automatically suppresses RuntimeWarnings for all tests.

    The fixture works by temporarily modifying the warnings filter to ignore
    any `RuntimeWarning` that may be raised during the test execution.
    """
    with warnings.catch_warnings():
        warnings.simplefilter("ignore", category=RuntimeWarning)

        # Yielding control to the test function so it can run with the modified filter
        yield


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_get(mocker):
    # Arrange: Mock the GET request using AsyncMock
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status = AsyncMock()

    # Patch httpx.AsyncClient and mock the 'get' method
    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 60, "proxy": None}

    # Act: Call the async function
    result = await request(url, options=options, axios_options=axios_options)

    # Assert: Verify the response is as expected
    assert await result == {"key": "value"}

    # Ensure that get was called with the correct parameters
    httpx.AsyncClient.get.assert_called_once_with(url, timeout=60, proxies=None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_post(mocker):
    # Arrange: Mock the POST request using httpx.AsyncClient
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "title": "foo"}
    mock_response.raise_for_status = AsyncMock()

    # Patch httpx.AsyncClient and mock the 'request' method for POST
    mocker.patch.object(httpx.AsyncClient, "request", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    data = {"title": "foo", "body": "bar", "userId": 1}
    options = {"method": "POST"}
    axios_options = {"timeout": 100, "proxy": None}

    # Act: Call the async function
    result = await request(url, data, options, axios_options)

    # Assert: Verify the response is as expected
    assert await result == {"id": 1, "title": "foo"}
    httpx.AsyncClient.request.assert_called_once_with("POST", url, json=data, timeout=100, proxies=None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_unsupported_method():
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "DELETE"}
    data = {"title": "foo"}

    # Act & Assert: Test that ValueError is raised
    with pytest.raises(ValueError, match="Unsupported method: DELETE"):
        await request(url, data=data, options=options)


@pytest.mark.unit
@pytest.mark.asyncio
# @pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_request_merge_axios_options(mocker):
    # Arrange: Mock the GET request using httpx.AsyncClient
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "merged"}
    mock_response.raise_for_status = AsyncMock()

    # Patch httpx.AsyncClient and mock the 'get' method
    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 30, "proxy": "http://proxy.com"}

    # Act: Call the async function with merged options
    result = await request(url, options=options, axios_options=axios_options)

    # Assert: Verify the merged timeout and proxy values
    assert await result == {"key": "merged"}
    httpx.AsyncClient.get.assert_called_once_with(url, timeout=30, proxies="http://proxy.com")


@pytest.mark.unit
@pytest.mark.asyncio
# @pytest.mark.filterwarnings("ignore::RuntimeWarning")
async def test_request_default_axios_options(mocker):
    # Arrange: Mock the GET request using httpx.AsyncClient
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "default"}
    mock_response.raise_for_status = AsyncMock()

    # Patch httpx.AsyncClient and mock the 'get' method
    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}

    # Act: Call the async function with default options
    result = await request(url, options=options)

    # Assert: Verify the default timeout and proxy values
    assert await result == {"key": "default"}
    httpx.AsyncClient.get.assert_called_once_with(url, timeout=60, proxies=None)
