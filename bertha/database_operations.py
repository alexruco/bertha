import time
import sys
from sqlite3 import dbapi2 as sqlite3
from urllib.parse import urlparse
from sqlalchemy.pool import QueuePool
from datetime import datetime, timedelta
from bertha.database_setup import initialize_database
from bertha.utils import get_robots, is_actual_page, normalize_url

# Create a connection pool
pool = QueuePool(lambda: sqlite3.connect('db_websites.db'), max_overflow=10, pool_size=5)

def get_conn(db_name='db_websites.db'):
    """
    Get a connection from the pool, using the specified database name.
    
    :param db_name: The name of the SQLite database file.
    :return: A connection object.
    """
    return sqlite3.connect(db_name)

def update_all_urls_indexibility(base_url, retries=5, timeout=2):
    """
    Updates the indexibility of all URLs in the database for the given base URL.
    
    :param base_url: The base URL of the website to check.
    :param retries: The number of retries for each operation if a timeout occurs.
    :param timeout: Time in seconds to wait between retries.
    """
    robots_rules = get_robots(base_url)
    if robots_rules is None:
        print(f"No robots.txt rules found for {base_url}. Skipping indexibility updates.")
        return

    conn = get_conn()
    cursor = conn.cursor()
    try:
        cursor.execute('SELECT url FROM tb_pages WHERE url LIKE ?', (f'%{base_url}%',))
        urls = cursor.fetchall()
    finally:
        conn.close()

    for url_tuple in urls:
        url = url_tuple[0]
        for attempt in range(retries):
            try:
                update_indexibility(url, robots_rules, db_name='db_websites.db')
                break
            except Exception as e:
                print(f"Updating indexibility for {url} failed, retrying {attempt + 1}/{retries}...")
                time.sleep(timeout)
        else:
            print(f"Failed to update indexibility for {url} after multiple attempts.")

def update_indexibility(url, robots_rules, db_name='db_websites.db'):
    """
    Updates the robots_index and robots_follow fields for a given URL in the database
    based on the robots.txt rules.

    :param url: The URL to update.
    :param robots_rules: A dictionary of robots.txt rules or None if robots.txt is inaccessible.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    if robots_rules is None:
        print(f"No robots.txt rules to apply for {url}. Skipping indexibility update.")
        return

    parsed_url = urlparse(url)
    path = parsed_url.path

    # Default to index and follow if no rules match
    index = True
    follow = True

    # Check against each rule in robots.txt
    for rule_path, rule_flags in robots_rules.items():
        if path.startswith(rule_path):
            index = rule_flags["index"]
            follow = rule_flags["follow"]
            break

    for i in range(5):
        try:
            with sqlite3.connect(db_name, timeout=30) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE tb_pages
                    SET robots_index = ?, robots_follow = ?
                    WHERE url = ?
                ''', (index, follow, url))
                print(f"Updated robots info for '{url}' with index: {index}, follow: {follow}.")
                conn.commit()
            break

        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i + 1}/5...")
                time.sleep(2)
            else:
                raise

def insert_if_not_exists(url, referring_page=None, db_name='db_websites.db', retries=5):
    # Normalize the URL to ensure consistency
    normalized_url = normalize_url(url)

    # Check if the URL is an actual page before proceeding
    if not is_actual_page(normalized_url):
        print(f"insert_if_not_exists: Skipping non-page URL: {normalized_url}")
        return

    for i in range(retries):
        try:
            with get_conn(db_name) as conn:
                cursor = conn.cursor()
                # Perform the check using the normalized URL
                cursor.execute('SELECT COUNT(*) FROM tb_pages WHERE url = ? OR url = ?', (normalized_url, normalized_url + '/'))
                count = cursor.fetchone()[0]

                if count == 0:
                    dt_discovered = datetime.now().strftime('%Y%m%d%H%M%S')
                    cursor.execute('''
                        INSERT INTO tb_pages (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code)
                        VALUES (?, ?, ?, ?, ?, ?)
                    ''', (normalized_url, dt_discovered, None, referring_page, False, 0))
                    print(f"Inserted '{normalized_url}' into 'tb_pages' with discovery timestamp '{dt_discovered}'.")
                else:
                    print(f"'{normalized_url}' or '{normalized_url}/' already exists in 'tb_pages'.")
            break
        except sqlite3.OperationalError as e:
            if 'locked' in str(e):
                print(f"Database is locked, retrying {i + 1}/{retries}...")
                time.sleep(2)  # wait before retrying, increase the sleep time if necessary
            else:
                raise
          
def update_sitemaps_for_url(url, sitemap_url,  db_name='db_websites.db'):
    conn = get_conn(db_name=db_name)
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
    with sqlite3.connect(db_name, timeout=30) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE tb_pages
            SET status_code = ?, dt_last_crawl = ?, successful_page_fetch = ?
            WHERE url = ?
        ''', (status_code, dt_last_crawl, successful, url))
        conn.commit()
        print(f"Updated crawl info for '{url}' with status {status_code}, dt_last_crawl {dt_last_crawl}, and successful_page_fetch {successful}.")



def get_urls_to_crawl(base_url, gap=30, db_name='db_websites.db'):
    # Calculate cutoff date
    if gap == 0:
        # Set cutoff to the start of today
        cutoff_date = datetime.now().strftime('%Y%m%d000000')
    else:
        # Set cutoff to the exact time X days ago
        cutoff_date = (datetime.now() - timedelta(days=gap)).strftime('%Y%m%d%H%M%S')

    conn = sqlite3.connect(db_name)
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
        conn.close()  # Close the connection

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

def fetch_all_website_data(base_url, db_name='db_websites.db'):
    """
    Fetches all data for a given website (base URL) from the database.

    :param base_url: The base URL of the website.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    :return: A list of dictionaries containing all data for each URL.
    """
    conn = get_conn(db_name=db_name)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code, dt_last_crawl, robots_index, robots_follow
            FROM tb_pages
            WHERE url LIKE ?
        ''', (f'%{base_url}%',))

        rows = cursor.fetchall()
        data = [
            {
                "url": row[0],
                "dt_discovered": row[1],
                "sitemaps": row[2],
                "referring_pages": row[3],
                "successful_page_fetch": row[4],
                "status_code": row[5],
                "dt_last_crawl": row[6],
                "robots_index": row[7],
                "robots_follow": row[8]
            }
            for row in rows
        ]
    finally:
        conn.close()

    return data

def fetch_url_data(url, db_name='db_websites.db'):
    """
    Fetches all data for a specific URL from the database.

    :param url: The specific URL.
    :param db_name: The name of the SQLite database file.
    :return: A dictionary containing all data for the URL.
    """
    conn = get_conn(db_name)  # Pass the db_name to get_conn
    cursor = conn.cursor()
    try:
        cursor.execute('''
            SELECT url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code, dt_last_crawl, robots_index, robots_follow
            FROM tb_pages
            WHERE url = ?
        ''', (url,))

        row = cursor.fetchone()
        if row:
            data = {
                "url": row[0],
                "dt_discovered": row[1],
                "sitemaps": row[2],
                "referring_pages": row[3],
                "successful_page_fetch": row[4],
                "status_code": row[5],
                "dt_last_crawl": row[6],
                "robots_index": row[7],
                "robots_follow": row[8]
            }
        else:
            data = None
    finally:
        conn.close()

    return data
