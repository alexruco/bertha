import pytest
from bertha.crawl_pages import crawl_pages, process_sitemaps, crawl_all_pages
from bertha.database_operations import insert_if_not_exists, fetch_all_website_data

@pytest.fixture(scope="module")
def base_url():
    return "https://example.com"

def test_process_sitemaps(base_url):
    process_sitemaps(base_url, retries=3, timeout=2)
    data = fetch_all_website_data(base_url)
    assert data is not None
    assert len(data) > 0

def test_crawl_all_pages(base_url):
    crawl_all_pages(base_url, gap=30, retries=3, timeout=2)
    data = fetch_all_website_data(base_url)
    assert data is not None
    assert len(data) > 0
