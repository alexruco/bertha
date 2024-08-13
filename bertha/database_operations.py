# bertha/database_operations.py

from sqlite3 import dbapi2 as sqlite3
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
import time

# Create a connection pool
pool = QueuePool(lambda: sqlite3.connect('db_websites.db'), max_overflow=10, pool_size=5)

def get_conn():
    """
    Get a connection from the pool.
    """
    return pool.connect()

def insert_if_not_exists(url, db_name='db_websites.db', retries=5):
    """
    Inserts a URL into the database if it does not already exist.

    :param url: The URL to be inserted.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    :param retries: The number of times to retry the operation if the database is locked (default is 5).
    """
    for i in range(retries):
        try:
            with sqlite3.connect(db_name, timeout=30) as conn:  # Increased timeout to 30 seconds
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM tb_pages WHERE url = ?', (url,))
                count = cursor.fetchone()[0]

                if count == 0:
                    dt_discovered = datetime.now().strftime('%Y%m%d%H%M%S')
                    cursor.execute('''
                        INSERT INTO tb_pages (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (url, dt_discovered, None, None, False, 0))
                    print(f"Inserted '{url}' into 'tb_pages' with discovery timestamp '{dt_discovered}'.")
                else:
                    print(f"'{url}' already exists in 'tb_pages'.")
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i+1}/{retries}...")
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

def update_crawl_info(url, status_code):
    conn = get_conn()
    cursor = conn.cursor()
    try:
        dt_last_crawl = datetime.now().strftime('%Y%m%d%H%M%S')
        
        cursor.execute('''
            UPDATE tb_pages
            SET status_code = ?, dt_last_crawl = ?
            WHERE url = ?
        ''', (status_code, dt_last_crawl, url))
        conn.commit()
    finally:
        conn.close()  # Return the connection to the pool

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
