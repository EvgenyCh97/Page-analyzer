import os
from collections import namedtuple

import requests
from dotenv import load_dotenv
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)

from . import db, parser, validator

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def get_main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('index.html', messages=messages)


@app.route('/urls', methods=['POST'])
def check_url():
    url = request.form.get('url')

    error = validator.validate_url(url)
    if error:
        error_message, category = error
        flash(error_message, category)
        messages = get_flashed_messages(with_categories=True)
        return render_template('index.html', messages=messages), 422

    connection = db.create_connection(DATABASE_URL)
    name = parser.extract_name(url)
    target_url = db.get_url_by_name(connection, name)
    if not target_url:
        url_id = db.add_url(connection, name).id
        flash('Страница успешно добавлена', 'success')
    else:
        flash('Страница уже существует', 'info')
        url_id = target_url.id
    db.close(connection)
    return redirect(url_for('get_url', id=url_id), code=302)


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    connection = db.create_connection(DATABASE_URL)
    url = db.get_url(connection, id)
    checks = db.get_url_checks(connection, id)
    db.close(connection)
    return render_template('url.html', messages=messages, url=url,
                           checks=checks)


@app.route('/urls')
def get_urls():
    connection = db.create_connection(DATABASE_URL)
    result = []
    urls, checks = db.get_urls(connection)
    if urls:
        checks = [check.status_code for check in checks]
        Record = namedtuple('Record',
                            ['id', 'name', 'created_at', 'status_code'])
        for i in range(0, len(urls)):
            url = urls[i]
            url_info = Record(url.id, url.name, url.created_at,
                              checks[i] if checks else None)
            result.append(url_info)
    db.close(connection)
    return render_template('urls.html', urls=result)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def run_check(id):
    connection = db.create_connection(DATABASE_URL)
    url = db.get_url(connection, id)
    try:
        page_data = parser.parse_site(url)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        db.add_url_check(connection, id, page_data)
        flash('Страница успешно проверена', 'success')
    db.close(connection)
    return redirect(url_for('get_url', id=id), code=302)
