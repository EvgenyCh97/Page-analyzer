from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract_name(url):
    return (urlparse(url)[0] + '://' + urlparse(url)[1]).lower()


def parse_site(url):
    try:
        r = requests.get(url.name)
        r.raise_for_status()
    except requests.exceptions.RequestException:
        raise requests.exceptions.RequestException
    else:
        status_code = r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.select_one('title')
        h1 = soup.select_one('h1')
        description = soup.select_one('meta[name="description"]')
    return status_code, title, h1, description
