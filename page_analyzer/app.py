import os
from datetime import date

import psycopg2
import psycopg2.extras
import requests
import validators
from dotenv import load_dotenv
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)

from . import db, parser

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


def make_connection(database_url):
    def wrapper(func):
        def inner(*args, **kwargs):
            with psycopg2.connect(database_url) as connection:
                return func(connection, *args, **kwargs)
        inner.__name__ = func.__name__
        return inner
    return wrapper


@app.route('/')
def get_main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['POST'])
@make_connection(DATABASE_URL)
def check_url(connection):
    url = request.form.get('url')

    for pass_check, message in ((url, 'URL обязателен'),
                                (validators.url(url), 'Некорректный URL')):
        if not pass_check:
            flash(message, 'danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template('main.html', messages=messages), 422

    name = parser.extract_name(url)
    checking_result = db.find_url(connection, name)
    if not checking_result:
        current_date = date.today().isoformat()
        db.add_url(connection, name, current_date)
        flash('Страница успешно добавлена', 'success')
        url_id = db.find_url(connection, name)['id']
    else:
        flash('Страница уже существует', 'info')
        url_id = checking_result['id']
    return redirect(url_for('get_url', id=url_id), code=302)


@app.route('/urls/<int:id>')
@make_connection(DATABASE_URL)
def get_url(connection, id):
    messages = get_flashed_messages(with_categories=True)
    url = db.get_url_from_db(connection, id)
    checks = db.get_url_checks(connection, id)
    return render_template('show.html', messages=messages, url=url,
                           checks=checks)


@app.route('/urls')
@make_connection(DATABASE_URL)
def get_urls(connection):
    urls = db.get_urls_list(connection)
    return render_template('index.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
@make_connection(DATABASE_URL)
def run_check(connection, id):
    url = db.get_url_from_db(connection, id)
    try:
        status_code, title, h1, description = parser.parse_site(url)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        current_date = date.today().isoformat()
        db.add_url_check(connection, id, status_code, h1, title, description,
                         current_date)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', id=id), code=302)
