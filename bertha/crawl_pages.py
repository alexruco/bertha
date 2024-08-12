# bertha/crawl_pages.py

from bertha.discover_pages import insert_if_not_exists
from bertha.utils import check_http_status
from bertha.database_setup import initialize_database
from hellen import internal_links_on_page
from datetime import datetime
import sqlite3

def crawl_pages(urls, db_name='db_websites.db'):
    """
    Crawls the provided collection of URLs, checking the status of pages and updating the database.
    
    :param urls: A collection of URLs to crawl.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    # Ensure the database is initialized
    initialize_database(db_name)

    # Connect to the database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    for url in urls:
        # Check the HTTP status of the URL
        status_code = check_http_status(url)
        dt_last_crawl = datetime.now().strftime('%Y%m%d%H%M%S')

        if status_code is None or status_code >= 400:
            # Update the HTTP status and dt_last_crawl in the database if the page is not available
            cursor.execute('''
                UPDATE tb_pages
                SET status_code = ?, dt_last_crawl = ?
                WHERE url = ?
            ''', (status_code, dt_last_crawl, url))
            print(f"Updated '{url}' with status {status_code} and dt_last_crawl {dt_last_crawl}.")
        else:
            # Page is available; get internal links
            internal_links = internal_links_on_page(url)

            # Insert each internal link if it doesn't already exist
            for link in internal_links:
                insert_if_not_exists(link, db_name)

            # Update the HTTP status and dt_last_crawl in the database for the crawled URL
            cursor.execute('''
                UPDATE tb_pages
                SET status_code = ?, dt_last_crawl = ?
                WHERE url = ?
            ''', (status_code, dt_last_crawl, url))
            print(f"Crawled and updated '{url}' with status {status_code} and dt_last_crawl {dt_last_crawl}.")

    # Commit changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()
