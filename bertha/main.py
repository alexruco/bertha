# bertha/main.py
import sys
from urllib.parse import urlparse
from .database_setup import initialize_database
from .discover_pages import insert_if_not_exists
from dourado import pages_from_sitemaps

def is_internal_url(base_url, url):
    """
    Checks if a given URL is internal to the base URL's domain.
    
    :param base_url: The base URL of the website.
    :param url: The URL to check.
    :return: True if the URL is internal, False otherwise.
    """
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    return base_domain == url_domain

def main():
    """
    Main function that initializes the database, processes the base URL, retrieves sitemaps,
    filters internal URLs, and processes them.
    """
    # Check if the base URL is provided as a command-line argument
    if len(sys.argv) != 2:
        print("Usage: python main.py <base_url>")
        sys.exit(1)

    base_url = sys.argv[1]

    # Initialize the database
    initialize_database()

    # Pass the base URL to the discover_pages function
    insert_if_not_exists(base_url)

    # Get the list of URLs from the sitemaps
    urls = pages_from_sitemaps(base_url)

    # Filter for internal URLs
    internal_urls = [url for url in urls if is_internal_url(base_url, url)]

    # Pass each internal URL to the discover_pages function
    for url in internal_urls:
        insert_if_not_exists(url)

if __name__ == "__main__":
    main()
