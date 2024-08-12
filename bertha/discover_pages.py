# bertha/discover_pages.py
import sqlite3
from datetime import datetime
from bertha.database_setup import initialize_database  # Adjusted import

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

def insert_if_not_exists(url, db_name='db_websites.db'):
    """
    Inserts the URL into tb_pages if it doesn't already exist, with a discovery timestamp.

    :param url: The URL of the website to insert.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    initialize_database(db_name)

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

if __name__ == "__main__":
    url = input("Enter the URL to discover: ")
    insert_if_not_exists(url)
