import psycopg2
import psycopg2.extras


def create_connection(db_url):
    return psycopg2.connect(db_url)


def close(connection):
    connection.close()


def get_url_by_name(connection, name):
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls WHERE name = %s', (name,))
        connection.commit()
        return cursor.fetchone()


def add_url(connection, name):
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute('INSERT INTO urls (name) VALUES (%s)',
                       (name,))
        connection.commit()


def get_url(connection, id):
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls WHERE id = %s', (id,))
        connection.commit()
        return cursor.fetchone()


def get_url_checks(connection, id):
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute(
            'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC',
            (id,))
        connection.commit()
        return cursor.fetchall()


def get_urls(connection):
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute('SELECT * FROM urls ORDER BY id DESC')
        urls = cursor.fetchall()
        cursor.execute(
            '''SELECT DISTINCT ON (url_id) id, url_id, status_code
            FROM url_checks ORDER BY url_id DESC, id DESC''')
        checks = cursor.fetchall()
        connection.commit()
        return urls, checks


def add_url_check(connection, id, page_data):
    status_code = page_data['status_code']
    h1 = page_data['h1']
    title = page_data['title']
    description = page_data['description']
    with connection.cursor(
            cursor_factory=psycopg2.extras.NamedTupleCursor) as cursor:
        cursor.execute(
            '''INSERT INTO url_checks (url_id, status_code, h1,
            title, description)
            VALUES (%s, %s, %s, %s, %s)''',
            (str(id), str(status_code),
             str(h1.string) if h1 else None,
             str(title.string) if title else None,
             str(description['content']) if description else None))
        connection.commit()
