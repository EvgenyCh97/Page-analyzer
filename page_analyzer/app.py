import os
from datetime import date

import requests
import validators
from dotenv import load_dotenv
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)

from . import data_handlers, db
from .db import (add_url, get_url_checks, get_url_from_db,
                 get_urls_list)

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')


@app.route('/')
def get_main_page():
    messages = get_flashed_messages(with_categories=True)
    return render_template('main.html', messages=messages)


@app.route('/urls', methods=['POST'])
def check_url():
    url = request.form.get('url')

    for pass_check, message in ((url, 'URL обязателен'),
                                (validators.url(url), 'Некорректный URL')):
        if not pass_check:
            flash(message, 'danger')
            messages = get_flashed_messages(with_categories=True)
            return render_template('main.html', messages=messages), 422

    name = data_handlers.extract_name(url)
    checking_result = db.find_url(name)
    if not checking_result:
        current_date = date.today().isoformat()
        add_url(name, current_date)
        flash('Страница успешно добавлена', 'success')
        url_id = db.find_url(name)[0]['id']
    else:
        flash('Страница уже существует', 'info')
        url_id = checking_result[0]['id']
    return redirect(url_for('get_url', id=url_id), code=302)


@app.route('/urls/<int:id>')
def get_url(id):
    messages = get_flashed_messages(with_categories=True)
    url = get_url_from_db(id)
    checks = get_url_checks(id)
    return render_template('show.html', messages=messages, url=url,
                           checks=checks)


@app.route('/urls')
def get_urls():
    urls = get_urls_list()
    return render_template('index.html', urls=urls)


@app.route('/urls/<int:id>/checks', methods=['POST'])
def run_check(id):
    site = get_url_from_db(id)
    try:
        status_code, title, h1, description = data_handlers.parse_site(site)
    except requests.exceptions.RequestException:
        flash('Произошла ошибка при проверке', 'danger')
    else:
        current_date = date.today().isoformat()
        db.add_url_check(id, status_code, h1, title, description, current_date)
        flash('Страница успешно проверена', 'success')
    return redirect(url_for('get_url', id=id), code=302)
