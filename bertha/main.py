# main.py

import sys
from bertha.utils import check_http_status
from bertha.crawl_pages import crawl_pages, crawl_all_pages, process_sitemaps
from bertha.database_operations import (
    insert_main_url,
    initialize_database_with_retries,
    update_all_urls_indexibility,
    fetch_all_website_data,
    fetch_url_data,
    update_crawl_info
)

def main(base_url, gap, retries=5, timeout=30):
    """
    Main function that initializes the database, stores the main URL, retrieves URLs from sitemaps,
    and processes them one by one.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated.
    :param retries: Number of retries for operations if a timeout occurs.
    :param timeout: Time in seconds to wait between retries.
    :return: The data of the website after crawling.
    """
    
    # Step 1: Initialize the database
    initialize_database_with_retries(retries, timeout)
    
    # Step 2: Insert the main URL
    insert_main_url(base_url, retries, timeout)
    
    # Step 3: Retrieve and insert URLs from sitemaps
    process_sitemaps(base_url, retries, timeout)
    
    # Step 4: Crawl the pages one by one
    crawl_all_pages(base_url, gap, retries, timeout)
    
    # Step 5: Update indexibility for all URLs
    print("Updating indexibility for all URLs...")
    update_all_urls_indexibility(base_url, retries, timeout)
    print("Indexibility update complete.")
    
    # Step 6: Return all data for the website
    return fetch_all_website_data(base_url)


def crawl_website(base_url, gap=30):
    """
    Initiates a crawl of the website starting from the base_url, using the provided gap.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated (default: 30 days).
    :return: The data of the website after crawling.
    """
    return main(base_url, gap)

def recrawl_website(base_url):
    """
    Forces a recrawl of the entire website by setting the gap to 0.
    
    :param base_url: The base URL of the website to recrawl.
    :return: The data of the website after recrawling.
    """
    return main(base_url, gap=0)

def recrawl_url(url, db_name='db_websites.db'):
    """
    Recrawls a specific URL, updating its status and related internal links in the database.
    
    :param url: The specific URL to recrawl.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    :return: The data of the specific URL after recrawling.
    """
    status_code = check_http_status(url)
    
    if status_code is None or status_code >= 400:
        # Handle non-available URL gracefully
        print(f"URL '{url}' is not available. Status code: {status_code}")
        update_crawl_info(url, status_code, successful=False, db_name=db_name)
        return None
    
    # Proceed with the regular crawl process
    crawl_pages([url], db_name)
    return fetch_url_data(url, db_name)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <base_url_or_url>")
        sys.exit(1)

    command = sys.argv[1]
    url = sys.argv[2]
    
    if command == "crawl":
        website_data = crawl_website(url)
        print(website_data)
    elif command == "recrawl":
        website_data = recrawl_website(url)
        print(website_data)
    elif command == "recrawl_url":
        url_data = recrawl_url(url)
        print(url_data)
    else:
        print("Unknown command. Use 'crawl', 'recrawl', or 'recrawl_url'.")
        sys.exit(1)
