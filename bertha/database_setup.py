# database_setup.py
import sqlite3
import os

def initialize_database(db_name='db_websites.db'):
    """
    Initializes the SQLite database and ensures that the required tables exist.
    
    :param db_name: Name of the SQLite database file (default is 'db_websites.db').
    """
    # Connect to the SQLite database (this will create the file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Create the tb_discovery table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_discovery (
            url TEXT NOT NULL,
            dt_discovered TEXT NOT NULL,  -- formatted as YYYYMMDDHHMMSS
            sitemaps TEXT,
            referring_pages TEXT,
            dt_last_crawl TEXT NOT NULL,  -- formatted as YYYYMMDDHHMMSS
            successful_page_fetch BOOLEAN NOT NULL,
            status_code INTEGER NOT NULL
        )
    ''')

    print("Table 'tb_discovery' is ready.")
    
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
