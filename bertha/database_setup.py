# bertha/database_setup.py
import sqlite3


def initialize_database(db_name='db_websites.db'):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    
    # Create the table with new columns for robots_index and robots_follow
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tb_pages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT UNIQUE NOT NULL,
            dt_discovered TEXT,
            sitemaps TEXT,
            referring_pages TEXT,
            successful_page_fetch BOOLEAN,
            status_code INTEGER,
            dt_last_crawl TEXT,
            robots_index BOOLEAN DEFAULT NULL,
            robots_follow BOOLEAN DEFAULT NULL
        )
    ''')
    conn.commit()
    cursor.close()
    conn.close()

if __name__ == "__main__":
    initialize_database()
