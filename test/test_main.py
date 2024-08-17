import pytest
from bertha.main import crawl_website, recrawl_website, recrawl_url
from bertha.database_operations import fetch_all_website_data, fetch_url_data, insert_if_not_exists
from unittest.mock import patch
from bertha.database_setup import initialize_database

@pytest.fixture(autouse=True)
def setup_database():
    initialize_database('test_db.db')

def test_recrawl_url():
    base_url = 'https://example.com'
    specific_url = f"{base_url}/specific-page"
    insert_if_not_exists(specific_url, db_name='test_db.db')  # Ensure URL is in the database

    # Mock check_http_status to return a 500 status code
    with patch('bertha.utils.check_http_status') as mock_check_http_status:
        mock_check_http_status.return_value = 500
        recrawl_url(specific_url, db_name='test_db.db')

        # Ensure the mock was called as expected
        mock_check_http_status.assert_called_with(specific_url)

    # Fetch the data from the database
    data = fetch_url_data(specific_url, db_name='test_db.db')
    print(f"DEBUG: Data fetched for {specific_url}: {data}")  # Debugging line

    # Assert that the status code is correctly recorded as 500
    assert data is not None  # Ensure data is returned
    assert data['status_code'] == 500  # Check that the status code is as expected
