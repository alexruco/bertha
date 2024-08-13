# bertha/crawl_pages.py

import time
import sqlite3
from datetime import datetime
from hellen import internal_links_on_page
from utils import check_http_status
from database_setup import initialize_database

from database_operations import (
    insert_if_not_exists,
    update_referring_pages,
    update_crawl_info
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
