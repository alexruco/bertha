# bertha/__init__.py

"""
Bertha Web Crawler Package
==========================

This package provides tools to crawl websites, manage the crawling process, and interact with a SQLite database to store and retrieve information about crawled pages.

Modules
-------
crawl_pages
    Contains the functions to crawl a list of URLs, check their HTTP status, and update the database accordingly.

database_operations
    Encapsulates all database operations, including inserting new records, updating existing records, and querying data.

database_setup
    Handles the initialization and setup of the SQLite database.

utils
    Provides utility functions, including checking the HTTP status of URLs.
"""

__version__ = "0.2.0"

# Import key functions at the package level for easier access
from bertha.database_setup import initialize_database
from bertha.database_operations import (
    insert_if_not_exists,
    update_sitemaps_for_url,
    update_crawl_info,
    get_urls_to_crawl
)
from bertha.crawl_pages import crawl_pages
from bertha.utils import check_http_status
from bertha.database_operations import get_urls_to_crawl
from bertha.main import (
    crawl_website,
    recrawl_website,
    recrawl_url
)


__all__ = [
    "initialize_database",
    "insert_if_not_exists",
    "update_sitemaps_for_url",
    "update_crawl_info",
    "get_urls_to_crawl",
    "crawl_pages",
    "check_http_status",
    "crawl_website",
    "recrawl_website",
    "recrawl_url"
]
