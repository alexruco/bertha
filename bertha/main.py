from dourado import pages_from_sitemaps
from bertha.discover_pages import insert_if_not_exists, update_sitemaps_for_url

def main(base_url):
    pages = pages_from_sitemaps(base_url)
    
    for url, sitemap_url in pages:
        # First, ensure the URL is inserted
        insert_if_not_exists(url)
        
        # Then, update the sitemaps field with the associated sitemap URL
        update_sitemaps_for_url(url, sitemap_url)

if __name__ == "__main__":
    base_url = "https://mysitefaster.com"  # Replace with your actual base URL
    main(base_url)
