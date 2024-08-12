# test_main.py
import unittest
from unittest.mock import patch, call
from bertha.main import main

class TestMain(unittest.TestCase):

    @patch('bertha.main.insert_if_not_exists')
    @patch('bertha.main.pages_from_sitemaps')
    def test_internal_url_processing(self, mock_pages, mock_insert):
        """
        Test that only internal URLs are processed from the sitemap.
        """
        base_url = 'https://example.com'
        mock_pages.return_value = [
            'https://example.com/page1',
            'https://example.com/page2',
            'https://external.com/page1'
        ]
        
        test_args = ['main.py', base_url]
        with patch('sys.argv', test_args):
            main()

        # Check that insert_into_discovery_if_not_exists was called with internal URLs only
        mock_insert.assert_has_calls([
            call('https://example.com'),
            call('https://example.com/page1'),
            call('https://example.com/page2')
        ], any_order=True)

        # Ensure the external URL was not processed
        calls = [call_args[0][0] for call_args in mock_insert.call_args_list]
        self.assertNotIn('https://external.com/page1', calls)

if __name__ == '__main__':
    unittest.main()
