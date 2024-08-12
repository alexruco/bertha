from urllib.parse import urlparse
from hellen import links_on_page
from virginia import check_page_availability
from dourado import website_sitemaps

def is_internal_url(base_url, url):
    """
    Checks if a given URL is internal to the base URL's domain.
    
    :param base_url: The base URL of the website.
    :param url: The URL to check.
    :return: True if the URL is internal, False otherwise.
    """
    base_domain = urlparse(base_url).netloc
    url_domain = urlparse(url).netloc
    return base_domain == url_domain
   