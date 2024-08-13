# bertha/crawl_pages.py

import time
import sys
import sqlite3
from datetime import datetime
from hellen import internal_links_on_page
from utils import check_http_status, get_robots
from database_setup import initialize_database
from dourado import pages_from_sitemaps
from hellen import internal_links_on_page

from database_operations import (
    insert_if_not_exists,
    update_referring_pages,
    update_crawl_info,
    update_sitemaps_for_url,
    get_urls_to_crawl,
    update_indexibility
)

def crawl_pages(urls, db_name='db_websites.db', retries=5):
    """
    Crawls the provided collection of URLs, checking the status of pages and updating the database.
    
    :param urls: A collection of URLs to crawl.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    :param retries: The number of times to retry the operation if the database is locked.
    """
    # Ensure the database is initialized
    initialize_database(db_name)

    for url in urls:
        # Attempt to crawl each URL, with retries in case of database locks
        for attempt in range(retries):
            try:
                # Check the HTTP status of the URL
                status_code = check_http_status(url)
                dt_last_crawl = datetime.now().strftime('%Y%m%d%H%M%S')
                successful = status_code == 200

                if status_code is None or status_code >= 400:
                    # Update the HTTP status and dt_last_crawl in the database if the page is not available
                    update_crawl_info(url, status_code, successful, db_name)
                    print(f"Updated '{url}' with status {status_code} and dt_last_crawl {dt_last_crawl}.")
                else:
                    # Page is available; get internal links
                    internal_links = internal_links_on_page(url)

                    # Insert each internal link if it doesn't already exist
                    for link in internal_links:
                        insert_if_not_exists(link, db_name=db_name)
                        # Update referring_pages for each existing link
                        update_referring_pages(link, url, db_name=db_name)

                    # Update the HTTP status, dt_last_crawl, and successful_page_fetch in the database for the crawled URL
                    update_crawl_info(url, status_code, successful, db_name)
                    print(f"Crawled and updated '{url}' with status {status_code} and dt_last_crawl {dt_last_crawl}.")

                break  # Break the retry loop if successful

            except sqlite3.OperationalError as e:
                if 'locked' in str(e):
                    print(f"Database is locked, retrying {attempt + 1}/{retries}...")
                    time.sleep(2)  # Wait before retrying, increase the sleep time if necessary
                else:
                    raise

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
