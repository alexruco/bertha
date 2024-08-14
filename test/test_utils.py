import pytest
from unittest.mock import patch
from bertha.utils import check_http_status, get_robots

@pytest.fixture(scope="module")
def base_url():
    return "https://example.com"

def test_check_http_status(base_url):
    status_code = check_http_status(base_url)
    assert status_code is not None
    assert status_code == 200

def test_get_robots(base_url):
    robots = get_robots(base_url)
    assert robots is not None
    assert isinstance(robots, dict)



@patch('bertha.utils.requests.get')
def test_get_robots(mock_get, base_url):
    # Mocking the response to return a sample robots.txt content
    mock_get.return_value.status_code = 200
    mock_get.return_value.text = "User-agent: *\nDisallow: /private/"
    
    robots = get_robots(base_url)
    assert robots is not None
    assert robots['/private/']['index'] == False
