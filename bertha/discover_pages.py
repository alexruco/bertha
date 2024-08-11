# discover_pages.py
import sqlite3
from datetime import datetime
from database_setup import initialize_database

def insert_into_discovery_if_not_exists(url, db_name='db_websites.db'):
    """
    Inserts the URL into tb_discovery if it doesn't already exist, with a discovery timestamp.
    
    :param url: The URL of the website to insert.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    # Ensure the database and tables are initialized
    initialize_database(db_name)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the URL already exists in tb_discovery
    cursor.execute('SELECT COUNT(*) FROM tb_discovery WHERE url = ?', (url,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert the URL into the table if it doesn't exist, along with the discovery timestamp
        dt_discovered = datetime.now().strftime('%Y%m%d%H%M%S')
        cursor.execute('''
            INSERT INTO tb_discovery (url, dt_discovered, sitemaps, referring_pages, successful_page_fetch, status_code)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (url, dt_discovered, None, None, False, 0))
        conn.commit()
        print(f"Inserted '{url}' into 'tb_discovery' with discovery timestamp '{dt_discovered}'.")
    else:
        print(f"'{url}' already exists in 'tb_discovery'.")

    # Close the cursor and connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    url = input("Enter the URL to discover: ")
    insert_into_discovery_if_not_exists(url)
