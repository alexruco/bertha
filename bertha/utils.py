# bertha/utils.py

import requests
from urllib.parse import urljoin

def get_robots(website):
    """
    Fetches and parses the robots.txt file for the given website.
    
    :param website: The base URL of the website (e.g., "https://example.com")
    :return: A dictionary of rules, where keys are paths and values are dictionaries with "index" and "follow" flags.
    """
    robots_url = urljoin(website, "/robots.txt")
    try:
        response = requests.get(robots_url, timeout=10)
        response.raise_for_status()

        robots_rules = {}
        for line in response.text.splitlines():
            line = line.strip()
            if line.lower().startswith("user-agent:"):
                # We only care about the global rules for all user agents
                user_agent = line.split(":")[1].strip().lower()
                if user_agent != "*":
                    continue
            elif line.lower().startswith("disallow:"):
                path = line.split(":")[1].strip()
                robots_rules[path] = {"index": False, "follow": False}
            elif line.lower().startswith("allow:"):
                path = line.split(":")[1].strip()
                robots_rules[path] = {"index": True, "follow": True}

        return robots_rules

    except requests.RequestException as e:
        print(f"Failed to fetch robots.txt for {website}: {e}")
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

# Example usage
if __name__ == "__main__":
    url = "https://www.example.com"
    status_code = check_http_status(url)
    if status_code is not None:
        print(f"The HTTP status code for {url} is {status_code}.")
    else:
        print(f"Failed to retrieve the HTTP status code for {url}.")

