# test/test_main.py

import pytest
from bertha.main import recrawl_url
from bertha.database_operations import fetch_url_data, insert_if_not_exists
from unittest.mock import patch
from bertha.database_setup import initialize_database

@pytest.fixture(autouse=True)
def setup_database():
    initialize_database('test_db.db')

def test_recrawl_url():
    base_url = 'https://example.com'
    specific_url = f"{base_url}/"
    insert_if_not_exists(specific_url, db_name='test_db.db')  # Ensure URL is in the database

    # Mock HTTP status to avoid 404 during testing
    with patch('bertha.utils.check_http_status') as mock_check_status:
        mock_check_status.return_value = 200  # Mocking a successful HTTP status
        recrawl_url(specific_url, db_name='test_db.db')  # Pass the correct db_name here

    # Fetch the data from the database
    data = fetch_url_data(specific_url, db_name='test_db.db')
    print(f"DEBUG: Data fetched for {specific_url}: {data}")  # Debugging line

    assert data is not None  # This should now pass as the URL was inserted
    assert data['status_code'] == 200  # Ensure the status code is as expected
    assert data['successful_page_fetch'] == 1  # Ensure the successful fetch is recorded
