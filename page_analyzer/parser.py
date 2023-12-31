from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup


def extract_name(url):
    parsing_result = urlparse(url)
    return f'{parsing_result[0]}://{parsing_result[1]}'.lower()


def parse_site(url):
    page_data = {}
    try:
        r = requests.get(url.name)
    except requests.exceptions.RequestException:
        return page_data
    else:
        soup = BeautifulSoup(r.text, 'html.parser')
        page_data['status_code'] = r.status_code
        page_data['title'] = soup.select_one('title')
        page_data['h1'] = soup.select_one('h1')
        page_data['description'] = soup.select_one('meta[name="description"]')
    return page_data
