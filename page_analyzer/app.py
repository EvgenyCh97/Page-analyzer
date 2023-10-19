import os

import validators
from dotenv import load_dotenv
from flask import (Flask, flash, get_flashed_messages, redirect,
                   render_template, request, url_for)

from .db import (add_url, add_url_check, get_url_checks, get_url_from_db,
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

    checking_result = add_url(url)
    url_id = checking_result['id']
    flash(checking_result['message'], checking_result['category'])
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
    checking_result = add_url_check(id)
    flash(checking_result['message'], checking_result['category'])
    return redirect(url_for('get_url', id=id), code=302)
