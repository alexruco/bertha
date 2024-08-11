# database_setup.py
import sqlite3
import os

def initialize_database(db_name='db_websites.db'):
    """
    Initializes the SQLite database and ensures that the required tables exist.
    
    :param db_name: Name of the SQLite database file (default is 'db_websites.db').
    """
    # Check if the database file exists
    db_exists = os.path.exists(db_name)

    # Connect to the SQLite database (this will create the file if it doesn't exist)
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # If the database file didn't exist, create the necessary tables
    if not db_exists:
        print(f"Database '{db_name}' created.")
    
    # Create the tb_discovery table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_discovery (
            url TEXT NOT NULL,
            sitemaps TEXT,
            referring_pages TEXT
        )
    ''')

    # Create the tb_crawl table if it doesn't exist
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_crawl (
            last_crawl TEXT NOT NULL,  -- formatted as YYYYMMDDHHMMSS
            successful_page_fetch BOOLEAN NOT NULL,
            status_code INTEGER NOT NULL
        )
    ''')

    print("Tables 'tb_discovery' and 'tb_crawl' are ready.")
    
    # Commit the changes and close the connection
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
