import unittest
from unittest.mock import patch, MagicMock
from bertha.main import crawl_website, recrawl_website, recrawl_url

class TestMain(unittest.TestCase):

    @patch('bertha.main.crawl_pages')
    @patch('bertha.main.get_urls_to_crawl')
    def test_crawl_website(self, mock_get_urls_to_crawl, mock_crawl_pages):
        # Setup mock return values
        mock_get_urls_to_crawl.return_value = ['https://www.example.com/page1', 'https://www.example.com/page2']
        
        # Call the function
        crawl_website('https://www.example.com', gap=30)
        
        # Assert that the get_urls_to_crawl was called with the correct parameters
        mock_get_urls_to_crawl.assert_called_once_with('https://www.example.com', 30)
        
        # Assert that crawl_pages was called with the correct URLs
        mock_crawl_pages.assert_called_once_with(['https://www.example.com/page1', 'https://www.example.com/page2'])

    @patch('bertha.main.crawl_pages')
    @patch('bertha.main.get_urls_to_crawl')
    def test_recrawl_website(self, mock_get_urls_to_crawl, mock_crawl_pages):
        # Setup mock return values
        mock_get_urls_to_crawl.return_value = ['https://www.example.com/page1', 'https://www.example.com/page2']
        
        # Call the function
        recrawl_website('https://www.example.com')
        
        # Assert that the get_urls_to_crawl was called with gap=0
        mock_get_urls_to_crawl.assert_called_once_with('https://www.example.com', 0)
        
        # Assert that crawl_pages was called with the correct URLs
        mock_crawl_pages.assert_called_once_with(['https://www.example.com/page1', 'https://www.example.com/page2'])

    @patch('bertha.main.crawl_pages')
    def test_recrawl_url(self, mock_crawl_pages):
        # Call the function
        recrawl_url('https://www.example.com/specific-page')
        
        # Assert that crawl_pages was called with the correct single URL
        mock_crawl_pages.assert_called_once_with(['https://www.example.com/specific-page'])

if __name__ == '__main__':
    unittest.main()
