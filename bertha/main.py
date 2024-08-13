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

def initialize_database_with_retries(retries, timeout):
    for attempt in range(retries):
        try:
            initialize_database()
            print("Database initialized successfully.")
            break
        except Exception as e:
            print(f"Database initialization failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to initialize the database after multiple attempts.")
        sys.exit(1)

def insert_main_url(base_url, retries, timeout):
    for attempt in range(retries):
        try:
            insert_if_not_exists(url=base_url)
            print(f"Inserted main URL: {base_url}")
            break
        except Exception as e:
            print(f"Inserting main URL failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to insert main URL after multiple attempts.")
        sys.exit(1)

def process_sitemaps(base_url, retries, timeout):
    for attempt in range(retries):
        try:
            urls_collected_from_sitemaps = pages_from_sitemaps(website_url=base_url)
            print(f"Retrieved URLs from sitemaps for {base_url}")
            break
        except Exception as e:
            print(f"Retrieving URLs from sitemaps failed, retrying {attempt + 1}/{retries}...")
            time.sleep(timeout)
    else:
        print("Failed to retrieve URLs from sitemaps after multiple attempts.")
        sys.exit(1)
    
    for url_from_sitemap, referring_sitemap in urls_collected_from_sitemaps:
        for attempt in range(retries):
            try:
                insert_if_not_exists(url=url_from_sitemap)
                update_sitemaps_for_url(url=url_from_sitemap, sitemap_url=referring_sitemap)
                print(f"Processed sitemap URL: {url_from_sitemap}")
                break
            except Exception as e:
                print(f"Processing {url_from_sitemap} failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print(f"Failed to process {url_from_sitemap} after multiple attempts.")

def crawl_all_pages(base_url, gap, retries, timeout):
    while True:
        for attempt in range(retries):
            try:
                urls = get_urls_to_crawl(base_url, gap)
                break
            except Exception as e:
                print(f"Retrieving URLs to crawl failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print("Failed to retrieve URLs to crawl after multiple attempts.")
            sys.exit(1)

        if not urls:
            print("No more URLs to crawl.")
            break

        for url in urls:
            for attempt in range(retries):
                try:
                    crawl_pages([url])
                    print(f"Crawled page: {url}")
                    break
                except Exception as e:
                    print(f"Crawling {url} failed, retrying {attempt + 1}/{retries}...")
                    time.sleep(timeout)
            else:
                print(f"Failed to crawl {url} after multiple attempts.")

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
