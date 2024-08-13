# bertha/database_setup.py
import sqlite3

# bertha/database_setup.py

import sqlite3
import os

import sqlite3

import sqlite3

def initialize_database(db_name='db_websites.db'):
    """
    Initializes the SQLite database by setting up the tables and applying necessary configurations.
    
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    conn = sqlite3.connect(db_name)
    
    # Set the database to use WAL mode for better concurrency.
    conn.execute('PRAGMA journal_mode=WAL;')
    
    cursor = conn.cursor()
    
    # Example of creating a table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS tb_pages (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url TEXT NOT NULL,
        dt_discovered TEXT,
        sitemaps TEXT,
        referring_pages TEXT,
        successful_page_fetch BOOLEAN,
        status_code INTEGER,
        dt_last_crawl TEXT
    )
    ''')
    
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
