# bertha/utils.py

import requests
from urllib.parse import urlparse


def check_http_status(url):
    """
    Returns the HTTP status code of the given URL.
    
    :param url: The URL to check the HTTP status for.
    :return: An integer representing the HTTP status code.
    """
    try:
        # Send a GET request to the URL
        response = requests.get(url, timeout=10)
        
        # Return the status code
        return response.status_code
    
    except requests.exceptions.RequestException as e:
        # If there's any exception (e.g., network error, invalid URL), return None or a custom code
        print(f"Error checking status for {url}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    url = "https://www.example.com"
    status_code = check_http_status(url)
    if status_code is not None:
        print(f"The HTTP status code for {url} is {status_code}.")
    else:
        print(f"Failed to retrieve the HTTP status code for {url}.")

