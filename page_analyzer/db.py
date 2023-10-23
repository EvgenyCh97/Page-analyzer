from datetime import date
from urllib.parse import urlparse

import requests
from bs4 import BeautifulSoup

from .db_handlers import insert_into_db, select_from_db


def add_url(url):
    result = {}
    name = (urlparse(url)[0] + '://' + urlparse(url)[1]).lower()
    if not select_from_db('SELECT * FROM urls WHERE name = %s', (name,)):
        current_date = date.today().isoformat()
        insert_into_db('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                       (name, current_date))
        result['message'] = 'Страница успешно добавлена'
        result['category'] = 'success'
    else:
        result['message'] = 'Страница уже существует'
        result['category'] = 'info'
    result['id'] = select_from_db('SELECT id FROM urls WHERE name = %s',
                                  (name,))[0]['id']
    return result


def get_url_from_db(id):
    return select_from_db('SELECT * FROM urls WHERE id = %s', (id,))[0]


def get_url_checks(id):
    return select_from_db(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC', (id,))


def get_urls_list():
    return select_from_db('SELECT DISTINCT ON (urls.id) urls.id, name, '
                          'url_checks.created_at, url_checks.status_code '
                          'FROM urls LEFT JOIN url_checks '
                          'ON urls.id = url_checks.url_id '
                          'ORDER BY urls.id DESC, url_checks.id DESC;')


def add_url_check(id):
    result = {}
    site = get_url_from_db(id)
    try:
        r = requests.get(site['name'])
        r.raise_for_status()
    except requests.exceptions.RequestException:
        result['message'] = 'Произошла ошибка при проверке'
        result['category'] = 'danger'
    else:
        status_code = r.status_code
        soup = BeautifulSoup(r.text, 'html.parser')
        title = soup.select_one('title')
        h1 = soup.select_one('h1')
        description = soup.select_one('meta[name="description"]')
        current_date = date.today().isoformat()
        insert_into_db('INSERT INTO url_checks (url_id, status_code, h1, '
                       'title, description, created_at)'
                       ' VALUES (%s, %s, %s, %s, %s, %s)',
                       (id, status_code,
                        h1.string if h1 else None,
                        title.string if title else None,
                        description['content'] if description else None,
                        current_date))
        result['message'] = 'Страница успешно проверена'
        result['category'] = 'success'
    return result
