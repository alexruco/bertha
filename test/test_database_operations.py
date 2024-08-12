import unittest
from unittest.mock import patch, MagicMock
from bertha.database_operations import (
    insert_if_not_exists,
    update_sitemaps_for_url,
    update_crawl_info,
    get_urls_to_crawl
)
from datetime import datetime, timedelta

class TestDatabaseOperations(unittest.TestCase):

    @patch('bertha.database_operations.sqlite3.connect')
    def test_insert_if_not_exists_inserts_new_url(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup: simulate the URL not being in the database
        mock_cursor.fetchone.return_value = [0]
        
        # Call the function
        insert_if_not_exists('https://www.example.com')
        
        # Verify that the insert was called
        mock_cursor.execute.assert_called_with(
            'INSERT INTO tb_pages (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code) VALUES (?, ?, ?, ?, ?, ?)',
            ('https://www.example.com', datetime.now().strftime('%Y%m%d%H%M%S'), None, None, False, 0)
        )

    @patch('bertha.database_operations.sqlite3.connect')
    def test_insert_if_not_exists_does_not_insert_existing_url(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup: simulate the URL already existing in the database
        mock_cursor.fetchone.return_value = [1]
        
        # Call the function
        insert_if_not_exists('https://www.example.com')
        
        # Verify that the insert was NOT called since the URL exists
        mock_cursor.execute.assert_called_once_with('SELECT COUNT(*) FROM tb_pages WHERE url = ?', ('https://www.example.com',))
        self.assertEqual(mock_cursor.execute.call_count, 1)

    @patch('bertha.database_operations.sqlite3.connect')
    def test_update_sitemaps_for_url(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup: simulate an existing sitemap
        mock_cursor.fetchone.return_value = ["https://www.example.com/sitemap.xml"]
        
        # Call the function
        update_sitemaps_for_url('https://www.example.com', 'https://www.example.com/new_sitemap.xml')
        
        # Verify that the update was called with the combined sitemaps
        mock_cursor.execute.assert_called_with(
            'UPDATE tb_pages SET sitemaps = ? WHERE url = ?',
            ('https://www.example.com/sitemap.xml,https://www.example.com/new_sitemap.xml', 'https://www.example.com')
        )

    @patch('bertha.database_operations.sqlite3.connect')
    def test_update_crawl_info(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the function
        update_crawl_info('https://www.example.com', 200)
        
        # Verify that the update was called with the correct parameters
        mock_cursor.execute.assert_called_with(
            'UPDATE tb_pages SET status_code = ?, dt_last_crawl = ? WHERE url = ?',
            (200, datetime.now().strftime('%Y%m%d%H%M%S'), 'https://www.example.com')
        )

    @patch('bertha.database_operations.sqlite3.connect')
    def test_get_urls_to_crawl(self, mock_connect):
        # Mocking the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Setup: simulate a result from the database query
        mock_cursor.fetchall.return_value = [('https://www.example.com/page1',), ('https://www.example.com/page2',)]
        
        # Call the function
        urls = get_urls_to_crawl('https://www.example.com', 30)
        
        # Verify that the query was called with the correct parameters
        cutoff_date = (datetime.now() - timedelta(days=30)).strftime('%Y%m%d%H%M%S')
        mock_cursor.execute.assert_called_with(
            '''
            SELECT url 
            FROM tb_pages 
            WHERE (dt_last_crawl IS NULL OR dt_last_crawl < ?)
            AND url LIKE ?
            ''',
            (cutoff_date, '%https://www.example.com%')
        )
        
        # Verify the returned URLs
        self.assertEqual(urls, ['https://www.example.com/page1', 'https://www.example.com/page2'])

if __name__ == '__main__':
    unittest.main()
