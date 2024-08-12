# test_crawl_pages.py

import unittest
from unittest.mock import patch, MagicMock
from bertha.crawl_pages import crawl_pages

class TestCrawlPages(unittest.TestCase):

    @patch('bertha.database_operations.update_crawl_info')
    @patch('bertha.crawl_pages.insert_if_not_exists')
    @patch('bertha.crawl_pages.internal_links_on_page')
    @patch('bertha.crawl_pages.check_http_status')
    def test_crawl_pages_successful(self, mock_check_http_status, mock_internal_links_on_page, mock_insert_if_not_exists, mock_update_crawl_info):
        mock_check_http_status.return_value = 200
        mock_internal_links_on_page.return_value = [
            "https://www.example.com/page1",
            "https://www.example.com/page2"
        ]
        
        crawl_pages(["https://www.example.com"])

        mock_check_http_status.assert_called_once_with("https://www.example.com")
        mock_internal_links_on_page.assert_called_once_with("https://www.example.com")
        mock_insert_if_not_exists.assert_any_call("https://www.example.com/page1", 'db_websites.db')
        mock_insert_if_not_exists.assert_any_call("https://www.example.com/page2", 'db_websites.db')
        mock_update_crawl_info.assert_called_once_with("https://www.example.com", 200)

    @patch('bertha.database_operations.update_crawl_info')
    @patch('bertha.crawl_pages.check_http_status')
    def test_crawl_pages_unsuccessful(self, mock_check_http_status, mock_update_crawl_info):
        mock_check_http_status.return_value = 404
        crawl_pages(["https://www.example.com/nonexistent"])

        mock_check_http_status.assert_called_once_with("https://www.example.com/nonexistent")
        mock_update_crawl_info.assert_called_once_with("https://www.example.com/nonexistent", 404)

if __name__ == '__main__':
    unittest.main()
