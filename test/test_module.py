# test_module.py
import unittest
import sqlite3
import os

from bertha.database_setup import initialize_database
from bertha.discover_pages import insert_into_discovery_if_not_exists

class TestDiscoverPages(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        """Set up a temporary database for testing."""
        cls.test_db = 'test_db_websites.db'
        initialize_database(cls.test_db)

    @classmethod
    def tearDownClass(cls):
        """Remove the temporary database after testing."""
        if os.path.exists(cls.test_db):
            os.remove(cls.test_db)

    def setUp(self):
        """Reset the database to a clean state before each test."""
        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('DELETE FROM tb_discovery')
        conn.commit()
        cursor.close()
        conn.close()

    def test_insert_new_url(self):
        """Test inserting a new URL into the tb_discovery table."""
        url = 'https://example.com'
        insert_into_discovery_if_not_exists(url, self.test_db)

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT url FROM tb_discovery WHERE url = ?', (url,))
        result = cursor.fetchone()
        cursor.close()
        conn.close()

        self.assertIsNotNone(result)
        self.assertEqual(result[0], url)

    def test_insert_existing_url(self):
        """Test that inserting an existing URL does not duplicate it."""
        url = 'https://example.com'
        insert_into_discovery_if_not_exists(url, self.test_db)
        insert_into_discovery_if_not_exists(url, self.test_db)

        conn = sqlite3.connect(self.test_db)
        cursor = conn.cursor()
        cursor.execute('SELECT COUNT(*) FROM tb_discovery WHERE url = ?', (url,))
        count = cursor.fetchone()[0]
        cursor.close()
        conn.close()

        self.assertEqual(count, 1)

if __name__ == '__main__':
    unittest.main()
