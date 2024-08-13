# main.py

import sys
import time
from crawl_pages import crawl_pages
from database_operations import (
    get_urls_to_crawl,
    insert_if_not_exists,
    update_sitemaps_for_url
)
from database_setup import initialize_database
from dourado import pages_from_sitemaps

def main(base_url, gap, retries=5, timeout=30):
    """
    Main function that initializes the database, retrieves URLs to crawl, and processes them.
    The function will continue to call `urls_to_crawl` and `crawl_pages` until no more URLs are returned.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated.
    :param retries: Number of retries for operations if a timeout occurs.
    :param timeout: Time in seconds to wait between retries.
    """
    
    # Initialize the database
    for attempt in range(retries):
        try:
            initialize_database()
            break
        except Exception as e:
            print(f"Database initialization failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to initialize the database after multiple attempts.")
        sys.exit(1)
    
    # Store the given URL if it doesn't already exist (e.g., the homepage)
    for attempt in range(retries):
        try:
            insert_if_not_exists(url=base_url)
            break
        except Exception as e:
            print(f"Inserting base URL failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to insert base URL after multiple attempts.")
        sys.exit(1)
    
    # Retrieve and store URLs from sitemaps
    for attempt in range(retries):
        try:
            urls_collected_from_sitemaps = pages_from_sitemaps(website_url=base_url)
            break
        except Exception as e:
            print(f"Retrieving URLs from sitemaps failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to retrieve URLs from sitemaps after multiple attempts.")
        sys.exit(1)
    
    # Iterate through the collected URLs and update the database
    for url_from_sitemap, referring_sitemap in urls_collected_from_sitemaps:
        for attempt in range(retries):
            try:
                # Insert the URL into the database
                insert_if_not_exists(url=url_from_sitemap)
                # Update the field "sitemaps"
                update_sitemaps_for_url(url=url_from_sitemap, sitemap_url=referring_sitemap)
                break
            except Exception as e:
                print(f"Updating database for {url_from_sitemap} failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print(f"Failed to update database for {url_from_sitemap} after multiple attempts.")
    
    # Recursively crawl the just inserted pages
    while True:
        for attempt in range(retries):
            try:
                # Get the URLs to crawl
                urls = get_urls_to_crawl(base_url, gap)
                break
            except Exception as e:
                print(f"Retrieving URLs to crawl failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print("Failed to retrieve URLs to crawl after multiple attempts.")
            sys.exit(1)

        # If no URLs are returned, break the loop
        if not urls:
            print("No more URLs to crawl.")
            break

        for attempt in range(retries):
            try:
                # Crawl the pages
                crawl_pages(urls)
                break
            except Exception as e:
                print(f"Crawling pages failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print("Failed to crawl pages after multiple attempts.")
            sys.exit(1)

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
    # Since we're recrawling a specific URL, we bypass urls_to_crawl and pass the single URL directly.
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
