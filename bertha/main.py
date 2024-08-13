# main.py

import sys
from crawl_pages import crawl_pages, crawl_all_pages, process_sitemaps
from database_operations import (
    insert_main_url,
    initialize_database_with_retries
)

def main(base_url, gap, retries=5, timeout=30):
    """
    Main function that initializes the database, stores the main URL, retrieves URLs from sitemaps,
    and processes them one by one.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated.
    :param retries: Number of retries for operations if a timeout occurs.
    :param timeout: Time in seconds to wait between retries.
    """
    
    # Step 1: Initialize the database
    initialize_database_with_retries(retries, timeout)
    
    # Step 2: Insert the main URL
    insert_main_url(base_url, retries, timeout)
    
    # Step 3: Retrieve and insert URLs from sitemaps
    process_sitemaps(base_url, retries, timeout)
    
    # Step 4: Crawl the pages one by one
    crawl_all_pages(base_url, gap, retries, timeout)


def crawl_website(base_url, gap=30):
    """
    Initiates a crawl of the website starting from the base_url, using the provided gap.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated (default: 30 days).
    """
    main(base_url, gap)

def recrawl_website(base_url):
    """
    Forces a recrawl of the entire website by setting the gap to 0.
    
    :param base_url: The base URL of the website to recrawl.
    """
    main(base_url, gap=0)

def recrawl_url(url, db_name='db_websites.db'):
    """
    Recrawls a specific URL, updating its status and related internal links in the database.
    
    :param url: The specific URL to recrawl.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    crawl_pages([url], db_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <base_url_or_url>")
        sys.exit(1)

    command = sys.argv[1]
    url = sys.argv[2]
    
    if command == "crawl":
        crawl_website(url)
    elif command == "recrawl":
        recrawl_website(url)
    elif command == "recrawl_url":
        recrawl_url(url)
    else:
        print("Unknown command. Use 'crawl', 'recrawl', or 'recrawl_url'.")
        sys.exit(1)