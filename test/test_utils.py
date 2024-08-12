import unittest
from unittest.mock import patch, MagicMock
from bertha.utils import check_http_status

class TestUtils(unittest.TestCase):

    @patch('bertha.utils.requests.get')
    def test_check_http_status_success(self, mock_get):
        # Simulate a successful HTTP response with status code 200
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_get.return_value = mock_response

        # Call the function with a URL
        status_code = check_http_status('https://www.example.com')

        # Verify that the status code is 200
        self.assertEqual(status_code, 200)
        mock_get.assert_called_once_with('https://www.example.com', timeout=10)

    @patch('bertha.utils.requests.get')
    def test_check_http_status_not_found(self, mock_get):
        # Simulate a 404 Not Found response
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_get.return_value = mock_response

        # Call the function with a URL
        status_code = check_http_status('https://www.example.com/nonexistent')

        # Verify that the status code is 404
        self.assertEqual(status_code, 404)
        mock_get.assert_called_once_with('https://www.example.com/nonexistent', timeout=10)

    @patch('bertha.utils.requests.get')
    def test_check_http_status_request_exception(self, mock_get):
        # Simulate a request exception (e.g., connection error, timeout)
        mock_get.side_effect = Exception('Connection error')

        # Call the function with a URL
        status_code = check_http_status('https://www.example.com')

        # Verify that the function returns None when an exception occurs
        self.assertIsNone(status_code)
        mock_get.assert_called_once_with('https://www.example.com', timeout=10)

if __name__ == '__main__':
    unittest.main()
