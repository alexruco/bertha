import unittest
from unittest.mock import patch, MagicMock
from bertha.database_setup import initialize_database

class TestDatabaseSetup(unittest.TestCase):

    @patch('bertha.database_setup.sqlite3.connect')
    def test_initialize_database_creates_table(self, mock_connect):
        # Mock the database connection and cursor
        mock_conn = MagicMock()
        mock_cursor = MagicMock()
        mock_connect.return_value = mock_conn
        mock_conn.cursor.return_value = mock_cursor
        
        # Call the initialize_database function
        initialize_database('test_db.db')
        
        # Verify that the database connection was established
        mock_connect.assert_called_once_with('test_db.db')
        
        # Verify that the cursor's execute method was called to create the table
        mock_cursor.execute.assert_called_once_with('''            
            CREATE TABLE IF NOT EXISTS tb_pages (
                url TEXT NOT NULL,
                dt_discovered TEXT NOT NULL,  -- formatted as YYYYMMDDHHMMSS
                sitemaps TEXT,
                referring_pages TEXT,
                dt_last_crawl TEXT,  -- Nullable, because it hasn't been crawled yet
                successful_page_fetch BOOLEAN NOT NULL,
                status_code INTEGER NOT NULL
            )
        ''')
        
        # Verify that changes were committed and the connection was closed
        mock_conn.commit.assert_called_once()
        mock_cursor.close.assert_called_once()
        mock_conn.close.assert_called_once()

if __name__ == '__main__':
    unittest.main()
