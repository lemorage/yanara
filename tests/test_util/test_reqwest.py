from unittest.mock import MagicMock

import pytest
import requests

from yanara.util.reqwest import request


@pytest.mark.unit
def test_request_get(mocker):
    # Arrange: Mock the GET request
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "value"}
    mocker.patch("requests.get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 60, "proxy": None}

    # Act: Call the function
    result = request(url, options=options, axios_options=axios_options)

    # Assert: Verify the response is as expected
    assert result == {"key": "value"}
    requests.get.assert_called_once_with(url, timeout=60, proxies=None)


@pytest.mark.unit
def test_request_post(mocker):
    # Arrange: Mock the POST request
    mock_response = MagicMock()
    mock_response.json.return_value = {"id": 1, "title": "foo"}
    mocker.patch("requests.request", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    data = {"title": "foo", "body": "bar", "userId": 1}
    options = {"method": "POST"}
    axios_options = {"timeout": 100, "proxy": None}

    # Act: Call the function
    result = request(url, data, options, axios_options)

    # Assert: Verify the response is as expected
    assert result == {"id": 1, "title": "foo"}
    requests.request.assert_called_once_with("POST", url, json=data, timeout=100, proxies=None)


@pytest.mark.unit
def test_request_unsupported_method():
    # Arrange
    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "DELETE"}
    data = {"title": "foo"}

    # Act & Assert: Test that ValueError is raised
    with pytest.raises(ValueError, match="Unsupported method: DELETE"):
        request(url, data=data, options=options)


@pytest.mark.unit
def test_request_merge_axios_options(mocker):
    # Arrange: Mock the GET request
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "merged"}
    mocker.patch("requests.get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}
    axios_options = {"timeout": 30, "proxy": "http://proxy.com"}

    # Act: Call the function with merged options
    result = request(url, options=options, axios_options=axios_options)

    # Assert: Verify the merged timeout and proxy values
    assert result == {"key": "merged"}
    requests.get.assert_called_once_with(url, timeout=30, proxies="http://proxy.com")


@pytest.mark.unit
def test_request_default_axios_options(mocker):
    # Arrange: Mock the GET request
    mock_response = MagicMock()
    mock_response.json.return_value = {"key": "default"}
    mocker.patch("requests.get", return_value=mock_response)

    url = "https://jsonplaceholder.typicode.com/posts"
    options = {"method": "GET"}

    # Act: Call the function with default options
    result = request(url, options=options)

    # Assert: Verify the default timeout and proxy values
    assert result == {"key": "default"}
    requests.get.assert_called_once_with(url, timeout=60, proxies=None)
