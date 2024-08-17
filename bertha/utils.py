# bertha/utils.py

import requests
from urllib.parse import urlparse

def parse_robots(robots_content):
    """
    Parses the content of a robots.txt file and returns a dictionary of rules.

    :param robots_content: The content of the robots.txt file as a string.
    :return: A dictionary where the keys are path prefixes and the values are dictionaries
             containing "index" and "follow" boolean flags.
    """
    rules = {}
    current_user_agent = None
    lines = robots_content.splitlines()

    for line in lines:
        line = line.strip()
        if not line or line.startswith('#'):  # Skip empty lines and comments
            continue

        if line.lower().startswith('user-agent:'):
            current_user_agent = line.split(':', 1)[1].strip()
        elif line.lower().startswith('disallow:') and current_user_agent == '*':
            path = line.split(':', 1)[1].strip()
            if path:  # If there's a specific path
                rules[path] = {"index": False, "follow": True}
        elif line.lower().startswith('allow:') and current_user_agent == '*':
            path = line.split(':', 1)[1].strip()
            if path:
                rules[path] = {"index": True, "follow": True}
        elif line.lower().startswith('crawl-delay:'):
            # Handle crawl-delay if needed
            pass

    return rules

def is_actual_page(url):
    """
    Determines if a URL is likely to be an actual page, not a file.
    Checks both the file extension and the content type.
    """
    # List of non-page file extensions to exclude
    NON_PAGE_EXTENSIONS = [
    '.xml', '.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg', 
    '.pdf', '.doc', '.docx', '.xls', '.xlsx', '.ppt', '.pptx', 
    '.zip', '.rar', '.exe', '.dmg', '.tar', '.gz'
    ]
    # Check if the URL ends with a known non-page extension
    if any(url.lower().endswith(ext) for ext in NON_PAGE_EXTENSIONS):
        return False

    # Optionally, check the content type by making a HEAD request
    content_type = get_content_type(url)
    if content_type and 'text/html' in content_type.lower():
        return True
    
    return False

def get_robots(base_url):
    """
    Fetches and parses the robots.txt file for a given base URL.

    :param base_url: The base URL of the website.
    :return: A dictionary of parsed robots.txt rules or None if the robots.txt file is not found.
    """
    parsed_url = urlparse(base_url)
    robots_url = f"{parsed_url.scheme}://{parsed_url.netloc}/robots.txt"

    try:
        response = requests.get(robots_url)
        response.raise_for_status()

        robots_content = response.text
        return parse_robots(robots_content)

    except requests.exceptions.RequestException as e:
        print(f"Failed to fetch robots.txt for {base_url}: {e}")
        return None

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

def get_content_type(url):
    """
    Performs a HEAD request to retrieve the Content-Type of the given URL.
    
    Args:
    url (str): The URL for which to retrieve the Content-Type.
    
    Returns:
    str: The Content-Type of the URL, or None if the request fails.
    """
    try:
        response = requests.head(url, allow_redirects=True)
        if response.status_code == 200:
            return response.headers.get('Content-Type')
        else:
            print(f"Failed to retrieve Content-Type for {url}: Status code {response.status_code}")
            return None
    except requests.RequestException as e:
        print(f"Error occurred while fetching Content-Type for {url}: {e}")
        return None

# Example usage
if __name__ == "__main__":
    url = "https://www.example.com"
    status_code = check_http_status(url)
    if status_code is not None:
        print(f"The HTTP status code for {url} is {status_code}.")
    else:
        print(f"Failed to retrieve the HTTP status code for {url}.")

