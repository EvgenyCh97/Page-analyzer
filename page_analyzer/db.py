from .db_handlers import insert_into_db, select_from_db


def find_url(name):
    return select_from_db('SELECT * FROM urls WHERE name = %s', (name,))


def add_url(name, current_date):
    insert_into_db('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                   (name, current_date))


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


def add_url_check(id, status_code, h1, title, description, current_date):
    insert_into_db('INSERT INTO url_checks (url_id, status_code, h1, '
                   'title, description, created_at)'
                   ' VALUES (%s, %s, %s, %s, %s, %s)',
                   (id, status_code,
                    h1.string if h1 else None,
                    title.string if title else None,
                    description['content'] if description else None,
                    current_date))
