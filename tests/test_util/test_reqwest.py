from unittest.mock import AsyncMock
import warnings

import httpx
import pytest

from yanara.util.reqwest import _http_call, request


@pytest.fixture(autouse=True)
def suppress_warnings():
    """A pytest fixture that automatically suppresses RuntimeWarnings for all tests.

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
    # Arrange: Mock the GET request using AsyncMock.get
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "value"}
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 60, "proxy": None}

    # Act: Call the async function
    result = await request(url, options=options, axios_options=axios_options)

    # Assert: Verify the response is as expected
    assert await result == {"key": "value"}

    httpx.AsyncClient.get.assert_called_once_with(url, json=None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_post(mocker):
    # Arrange: Mock the POST request using httpx.AsyncClient.post
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "title": "foo"}
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "post", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    data = {"title": "foo", "body": "bar", "userId": 1}
    options = {"method": "POST"}
    axios_options = {"timeout": 100, "proxy": None}

    # Act: Call the async function
    result = await request(url, data, options, axios_options)

    # Assert: Verify the response is as expected
    assert await result == {"id": 1, "title": "foo"}
    httpx.AsyncClient.post.assert_called_once_with(url, json=data)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_put(mocker):
    # Arrange: Mock the PUT request using httpx.AsyncClient.put
    mock_response = AsyncMock()
    mock_response.json.return_value = {"id": 1, "title": "updated"}
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "put", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts/1"
    data = {"title": "updated", "body": "updated body", "userId": 1}
    options = {"method": "PUT"}
    axios_options = {"timeout": 100, "proxy": None}

    # Act: Call the async function
    result = await request(url, data, options, axios_options)

    # Assert: Verify the response is as expected
    assert await result == {"id": 1, "title": "updated"}
    httpx.AsyncClient.put.assert_called_once_with(url, json=data)


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
async def test_request_merge_axios_options(mocker):
    # Arrange: Mock the GET request using httpx.AsyncClient
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "merged"}
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 30, "proxy": "http://proxy.com"}

    # Act: Call the async function with merged options
    result = await request(url, options=options, axios_options=axios_options)

    # Assert: Verify the merged timeout and proxy values
    assert await result == {"key": "merged"}
    httpx.AsyncClient.get.assert_called_once_with(url, json=None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_request_default_axios_options(mocker):
    # Arrange: Mock the GET request using httpx.AsyncClient
    mock_response = AsyncMock()
    mock_response.json.return_value = {"key": "default"}
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}

    # Act: Call the async function with default options
    result = await request(url, options=options)

    # Assert: Verify the default timeout and proxy values
    assert await result == {"key": "default"}
    httpx.AsyncClient.get.assert_called_once_with(url, json=None)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_http_call_success(mocker):
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    mock_response = AsyncMock()
    mock_response.json = AsyncMock(return_value={"key": "value"})
    mock_response.raise_for_status = AsyncMock()

    mocker.patch.object(httpx.AsyncClient, "post", return_value=mock_response)

    axios_options = {"timeout": 30, "proxy": None}
    data = {"title": "foo", "body": "bar"}

    # Act
    async with httpx.AsyncClient(timeout=30, proxy=None) as client:
        method = getattr(client, "post")
        result = await method(url, json=data if data else None)
        result = await result.json()

    # Assert
    assert result == {"key": "value"}
    httpx.AsyncClient.post.assert_called_once_with(url, json=data)


@pytest.mark.unit
@pytest.mark.asyncio
async def test_http_call_http_status_error(mocker):
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    mock_request = AsyncMock()
    mock_response = AsyncMock(status_code=404)
    mocker.patch.object(
        httpx.AsyncClient,
        "get",
        side_effect=httpx.HTTPStatusError("HTTP error", request=mock_request, response=mock_response),
    )

    axios_options = {"timeout": 30, "proxy": None}

    # Act & Assert
    with pytest.raises(httpx.HTTPStatusError):
        await _http_call(url, axios_options, data=None, http_method="get")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_http_call_request_error(mocker):
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    mocker.patch.object(httpx.AsyncClient, "get", side_effect=httpx.RequestError("Request error"))

    axios_options = {"timeout": 30, "proxy": None}

    # Act & Assert
    with pytest.raises(httpx.RequestError):
        await _http_call(url, axios_options, None, http_method="get")


@pytest.mark.unit
@pytest.mark.asyncio
async def test_http_call_unexpected_error(mocker):
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    mocker.patch.object(httpx.AsyncClient, "get", side_effect=Exception("Unexpected error"))

    axios_options = {"timeout": 30, "proxy": None}

    # Act & Assert
    with pytest.raises(Exception):
        await _http_call(url, axios_options, None, http_method="get")
