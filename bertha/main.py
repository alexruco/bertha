import sys
from crawl_pages import crawl_pages
from database_operations import (
    get_urls_to_crawl,
    insert_if_not_exists,
    update_sitemaps_for_url
)
from database_setup import initialize_database
from dourado import pages_from_sitemaps



def main(base_url, gap):
    """
    Main function that initializes the database, retrieves URLs to crawl, and processes them.
    The function will continue to call `urls_to_crawl` and `crawl_pages` until no more URLs are returned.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated.
    """
    
    #initialize the database
    initialize_database()
    
    #store the given url if not existis e.g. the homepage
    insert_if_not_exists(url=base_url)
    
    #retrieve and store urls from sitemaps
    urls_collected_from_sitemaps = pages_from_sitemaps(website_url=base_url)
    
    urls_from_sitemap, refering_sitemaps = urls_collected_from_sitemaps
    
    for url_from_sitemap in urls_from_sitemap:
        insert_if_not_exists(url=url_from_sitemap)
        update_sitemaps_for_url(url=url_from_sitemap, sitemap_url=refering_sitemaps)

    
    #recursivally crawl the just inserted pages
    while True:
        # Get the URLs to crawl
        urls = get_urls_to_crawl(base_url, gap)

        # If no URLs are returned, break the loop
        if not urls:
            print("No more URLs to crawl.")
            break

        # Crawl the pages
        crawl_pages(urls)

def crawl_website(base_url, gap=30):
    """
    Initiates a crawl of the website starting from the base_url, using the provided gap.
    
    :param base_url: The base URL of the website to crawl.
    :param gap: The number of days to check if the URL's last crawl is outdated (default: 30 days).
    """
    main(base_url, gap)

def recrawl_website(base_url):
    """
    Forces a recrawl of the entire website by setting the gap to 0.
    
    :param base_url: The base URL of the website to recrawl.
    """
    main(base_url, gap=0)

def recrawl_url(url, db_name='db_websites.db'):
    """
    Recrawls a specific URL, updating its status and related internal links in the database.
    
    :param url: The specific URL to recrawl.
    :param db_name: The name of the SQLite database file (default is 'db_websites.db').
    """
    # Since we're recrawling a specific URL, we bypass urls_to_crawl and pass the single URL directly.
    crawl_pages([url], db_name)

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py <command> <base_url_or_url>")
        sys.exit(1)

    command = sys.argv[1]
    url = sys.argv[2]

    if command == "crawl":
        crawl_website(url)
    elif command == "recrawl":
        recrawl_website(url)
    elif command == "recrawl_url":
        recrawl_url(url)
    else:
        print("Unknown command. Use 'crawl', 'recrawl', or 'recrawl_url'.")
        sys.exit(1)
