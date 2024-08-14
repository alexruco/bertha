import pytest
import sqlite3
from bertha.database_setup import initialize_database

@pytest.fixture(scope="module")
def db_name():
    return "test_db_websites.db"

def test_initialize_database(db_name):
    # Initialize the database
    initialize_database(db_name)

    # Connect to the database and verify the table exists
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()

    # Verify the table creation
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='tb_pages';")
    table_exists = cursor.fetchone()

    assert table_exists is not None, "Table 'tb_pages' should exist."

    # Verify the columns in the table
    cursor.execute("PRAGMA table_info(tb_pages);")
    columns = cursor.fetchall()

    expected_columns = {
        "id", "url", "dt_discovered", "sitemaps", "referring_pages",
        "successful_page_fetch", "status_code", "dt_last_crawl",
        "robots_index", "robots_follow"
    }

    column_names = {column[1] for column in columns}
    assert expected_columns.issubset(column_names), f"Expected columns {expected_columns} not found in table."

    cursor.close()
    conn.close()

def test_cleanup(db_name):
    """Clean up the test database file after tests."""
    import os
    if os.path.exists(db_name):
        os.remove(db_name)

