# test/test_database_operations.py

import pytest
from unittest.mock import patch
from bertha.database_setup import initialize_database
from bertha.database_operations import (
    insert_if_not_exists, 
    update_sitemaps_for_url, 
    update_crawl_info, 
    get_urls_to_crawl, 
    update_referring_pages, 
    fetch_all_website_data, 
    fetch_url_data
)

@pytest.fixture(autouse=True)
def setup_database():
    initialize_database('test_db.db')
    insert_if_not_exists('https://example.com', db_name='test_db.db')
    insert_if_not_exists('https://example.com/page1', db_name='test_db.db')
    insert_if_not_exists('https://example.com/page2', db_name='test_db.db')

def test_get_urls_to_crawl():
    # Adjust the gap to 0 for testing, so it includes all entries regardless of the last crawl date
    urls = get_urls_to_crawl('https://example.com', gap=0, db_name='test_db.db')
    assert urls is not None
    assert len(urls) > 0  # This should now pass

def test_update_crawl_info():
    insert_if_not_exists('https://example.com', db_name='test_db.db')
    update_crawl_info('https://example.com', 200, True, db_name='test_db.db')
    data = fetch_url_data('https://example.com', db_name='test_db.db')
    assert data is not None
    assert data['status_code'] == 200
