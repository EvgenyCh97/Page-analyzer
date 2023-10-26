import os
from datetime import date

import requests
import validators
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
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['POST'])
def check_url():
    url = request.form.get('url')

    errors = validator.validate_url(url)
    if errors:
        error_message, category = errors
        flash(error_message, category)
        messages = get_flashed_messages(with_categories=True)
        return render_template('main.html', messages=messages), 422

    connection = db.create_connection(DATABASE_URL)
    name = parser.extract_name(url)
    checking_result = db.get_url_by_name(connection, name)
    if not checking_result:
        current_date = date.today().isoformat()
        db.add_url(connection, name, current_date)
        flash('Страница успешно добавлена', 'success')
        url_id = db.get_url_by_name(connection, name).id
    else:
        flash('Страница уже существует', 'info')
        url_id = checking_result.id
    db.close(connection)
    return redirect(url_for('get_url', id=url_id), code=302)


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    connection = db.create_connection(DATABASE_URL)
    url = db.get_url(connection, id)
    checks = db.get_url_checks(connection, id)
    db.close(connection)
    return render_template('show.html', messages=messages, url=url,
                           checks=checks)


@app.route('/urls')
def get_urls():
    connection = db.create_connection(DATABASE_URL)
    urls = db.get_urls(connection)
    db.close(connection)
    return render_template('index.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def run_check(id):
    connection = db.create_connection(DATABASE_URL)
    url = db.get_url(connection, id)
    try:
        status_code, title, h1, description = parser.parse_site(url)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        current_date = date.today().isoformat()
        db.add_url_check(connection, id, status_code, h1, title, description,
                         current_date)
        flash('Страница успешно проверена', 'success')
    db.close(connection)
    return redirect(url_for('get_url', id=id), code=302)
