# bertha/database_operations.py

from sqlite3 import dbapi2 as sqlite3
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
from database_setup import initialize_database
import time
import sys

# Create a connection pool
pool = QueuePool(lambda: sqlite3.connect('db_websites.db'), max_overflow=10, pool_size=5)

def get_conn():
    """
    Get a connection from the pool.
    """
    return pool.connect()

def insert_if_not_exists(url, referring_page=None, db_name='db_websites.db', retries=5):
    for i in range(retries):
        try:
            with sqlite3.connect(db_name, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM tb_pages WHERE url = ?', (url,))
                count = cursor.fetchone()[0]

                if count == 0:
                    dt_discovered = datetime.now().strftime('%Y%m%d%H%M%S')
                    cursor.execute('''
                        INSERT INTO tb_pages (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (url, dt_discovered, None, referring_page, False, 0))
                    print(f"Inserted '{url}' into 'tb_pages' with discovery timestamp '{dt_discovered}'.")
                else:
                    print(f"'{url}' already exists in 'tb_pages'.")
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i + 1}/{retries}...")
                time.sleep(2)  # wait before retrying, increase the sleep time if necessary
            else:
                raise
                      
def update_sitemaps_for_url(url, sitemap_url):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT sitemaps FROM tb_pages WHERE url = ?', (url,))
        row = cursor.fetchone()

        if row:
            existing_sitemaps = row[0]
            if existing_sitemaps:
                new_sitemaps = f"{existing_sitemaps},{sitemap_url}"
            else:
                new_sitemaps = sitemap_url
            
            cursor.execute('''
                UPDATE tb_pages
                SET sitemaps = ?
                WHERE url = ?
            ''', (new_sitemaps, url))
            conn.commit()
            print(f"Updated 'sitemaps' field for '{url}'.")
    finally:
        conn.close()  # Return the connection to the pool

def update_crawl_info(url, status_code, successful, db_name='db_websites.db'):
    """
    Updates the crawl information for a given URL in the database.

    :param url: The URL to update.
    :param status_code: The HTTP status code returned by the URL.
    :param successful: Boolean indicating whether the page fetch was successful.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    dt_last_crawl = datetime.now().strftime('%Y%m%d%H%M%S')
    for i in range(5):
        try:
            with sqlite3.connect(db_name, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tb_pages
                    SET status_code = ?, dt_last_crawl = ?, successful_page_fetch = ?
                    WHERE url = ?
                ''', (status_code, dt_last_crawl, successful, url))
                print(f"Updated crawl info for '{url}' with status {status_code}, dt_last_crawl {dt_last_crawl}, and successful_page_fetch {successful}.")
                conn.commit()
            break  # Exit the retry loop if successful

        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i + 1}/5...")
                time.sleep(2)  # Wait before retrying, increase the sleep time if necessary
            else:
                raise

def get_urls_to_crawl(base_url, gap=30):
    cutoff_date = (datetime.now() - timedelta(days=gap)).strftime('%Y%m%d%H%M%S')
    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT url 
            FROM tb_pages 
            WHERE (dt_last_crawl IS NULL OR dt_last_crawl < ?)
            AND url LIKE ?
        ''', (cutoff_date, f'%{base_url}%'))

        urls = cursor.fetchall()
    finally:
        conn.close()  # Return the connection to the pool

    return [url[0] for url in urls]

def update_referring_pages(url, referring_url, db_name='db_websites.db'):
    """
    Updates the referring_pages field for a given URL in the database by appending a new referring URL.

    :param url: The URL for which to update the referring pages.
    :param referring_url: The URL of the page that refers to the target URL.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    for i in range(5):
        try:
            with sqlite3.connect(db_name, timeout=30) as conn:
                cursor = conn.cursor()

                cursor.execute('SELECT referring_pages FROM tb_pages WHERE url = ?', (url,))
                row = cursor.fetchone()

                if row:
                    existing_referring_pages = row[0]
                    if existing_referring_pages:
                        new_referring_pages = f"{existing_referring_pages},{referring_url}"
                    else:
                        new_referring_pages = referring_url
                    
                    cursor.execute('''
                        UPDATE tb_pages
                        SET referring_pages = ?
                        WHERE url = ?
                    ''', (new_referring_pages, url))
                    print(f"Updated 'referring_pages' for '{url}' with new referrer '{referring_url}'.")

                conn.commit()
            break  # Exit the retry loop if successful

        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i + 1}/5...")
                time.sleep(2)  # Wait before retrying, increase the sleep time if necessary
            else:
                raise

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
