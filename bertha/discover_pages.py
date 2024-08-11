# discover_pages.py
import sqlite3
from database_setup import initialize_database

def insert_into_discovery_if_not_exists(url, db_name='db_websites.db'):
    """
    Inserts the url into tb_urls if it doesn't already exist.
    
    :param url: The URL of the website to insert.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    # Ensure the database and tables are initialized
    initialize_database(db_name)

    # Connect to the SQLite database
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Check if the url already exists in tb_urls
    cursor.execute('SELECT COUNT(*) FROM tb_urls WHERE url = ?', (url,))
    count = cursor.fetchone()[0]

    if count == 0:
        # Insert the url into the table if it doesn't exist
        cursor.execute('INSERT INTO tb_urls (url) VALUES (?)', (url,))
        conn.commit()
        print(f"Inserted '{url}' into 'tb_urls'.")
    else:
        print(f"'{url}' already exists in 'tb_urls'.")

    # Close the cursor and connection
    cursor.close()
    conn.close()

if __name__ == "__main__":
    url = input("Enter the URL to discover: ")
    insert_into_discovery_if_not_exists(url)
