import os
from datetime import date
from urllib.parse import urlparse

import requests
import validators
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)

from .database_handlers import insert_into_db, select_from_db

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def get_main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['POST'])
def check_site():
    url = request.form.get('url')

    if not url:
        flash('URL обязателен', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422
    if not validators.url(url):
        flash('Некорректный URL', 'danger')
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    name = (urlparse(url)[0] + '://' + urlparse(url)[1]).lower()
    if not select_from_db('SELECT * FROM urls WHERE name = %s', (name,)):
        current_date = date.today().isoformat()
        insert_into_db('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                       (name, current_date))
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
    id = select_from_db(
        'SELECT id FROM urls WHERE name = %s', (name,))[0]['id']
    return redirect(url_for('get_site', id=id), code=302)


@app.route('/urls/<int:id>')
def get_site(id):
    messages = get_flashed_messages(with_categories=True)
    site = select_from_db('SELECT * FROM urls WHERE id = %s', (id,))[0]
    checks = select_from_db(
        'SELECT * FROM url_checks WHERE url_id = %s ORDER BY id DESC', (id,))
    return render_template('show.html', messages=messages, site=site,
                           checks=checks)


@app.route('/urls')
def get_urls():
    sites = select_from_db('SELECT DISTINCT ON (urls.id) urls.id, name, '
                           'url_checks.created_at, url_checks.status_code '
                           'FROM urls LEFT JOIN url_checks '
                           'ON urls.id = url_checks.url_id '
                           'ORDER BY urls.id DESC, url_checks.id DESC;')
    return render_template('index.html', sites=sites)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def get_check(id):
    site = select_from_db('SELECT * FROM urls WHERE id = %s', (id,))[0]
    url_id = site['id']
    try:
        r = requests.get(site['name'])
        r.raise_for_status()
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
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
                       (url_id, status_code,
                        h1.string if h1 else None,
                        title.string if title else None,
                        description['content'] if description else None,
                        current_date))
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_site', id=id), code=302)
