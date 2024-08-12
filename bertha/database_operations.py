# bertha/database_operations.py

import sqlite3
from datetime import datetime, timedelta  # Added timedelta importfrom bertha.database_setup import initialize_database  # Adjusted import

def insert_if_not_exists(url, db_name='db_websites.db'):
    """
    Inserts the URL into tb_pages if it doesn't already exist, with a discovery timestamp.

    :param url: The URL of the website to insert.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('SELECT COUNT(*) FROM tb_pages WHERE url = ?', (url,))
    count = cursor.fetchone()[0]

    if count == 0:
        dt_discovered = datetime.now().strftime('%Y%m%d%H%M%S')
        cursor.execute('''
            INSERT INTO tb_pages (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (url, dt_discovered, None, None, False, 0))
        conn.commit()
        print(f"Inserted '{url}' into 'tb_pages' with discovery timestamp '{dt_discovered}'.")
    else:
        print(f"'{url}' already exists in 'tb_pages'.")

    cursor.close()
    conn.close()

def update_sitemaps_for_url(url, sitemap_url, db_name='db_websites.db'):
    """
    Updates the sitemaps field for a given URL in the database.

    :param url: The URL for which to update the sitemaps.
    :param sitemap_url: The sitemap URL to add.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

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

    cursor.close()
    conn.close()

def update_crawl_info(url, status_code, db_name='db_websites.db'):
    """
    Updates the HTTP status code and the last crawl date for a given URL.

    :param url: The URL for which to update the information.
    :param status_code: The HTTP status code to record.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    dt_last_crawl = datetime.now().strftime('%Y%m%d%H%M%S')
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        UPDATE tb_pages
        SET status_code = ?, dt_last_crawl = ?
        WHERE url = ?
    ''', (status_code, dt_last_crawl, url))

    conn.commit()
    cursor.close()
    conn.close()

def urls_to_crawl(base_url, gap=30, db_name='db_websites.db'):
    """
    Returns a list of URLs that either haven't been crawled yet or whose last crawl
    was older than the specified gap (in days).
    
    :param base_url: The base URL of the website to filter internal URLs.
    :param gap: The number of days to check if the URL's last crawl is outdated.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    :return: A list of URLs that need to be crawled.
    """
    cutoff_date = (datetime.now() - timedelta(days=gap)).strftime('%Y%m%d%H%M%S')

    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    cursor.execute('''
        SELECT url 
        FROM tb_pages 
        WHERE (dt_last_crawl IS NULL OR dt_last_crawl < ?)
        AND url LIKE ?
    ''', (cutoff_date, f'%{base_url}%'))

    urls = cursor.fetchall()
    cursor.close()
    conn.close()

    return [url[0] for url in urls]
