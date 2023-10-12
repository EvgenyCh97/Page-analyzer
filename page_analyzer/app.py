import psycopg2
import psycopg2.extras
import os
from dotenv import load_dotenv
from flask import Flask, render_template, request, redirect, url_for, get_flashed_messages, flash
import validators
from urllib.parse import urlparse
from datetime import date

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY')
DATABASE_URL = os.getenv('DATABASE_URL')


@app.route('/')
def get_main_page():
    return render_template('main.html')


@app.route('/urls', methods=['POST'])
def check_site():
    url = request.form.get('url')

    if not url:
        return render_template('main.html', error='URL обязателен'), 422
    if not validators.url(url):
        return render_template('main.html', error='Некорректный URL'), 422

    name = (urlparse(url)[0] + '://' + urlparse(url)[1]).lower()
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE name = %s', (name,))
            if cursor.fetchone() is None:
                current_date = date.today().isoformat()
                cursor.execute(
                    'INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                    (name, current_date))
                connection.commit()
                flash('Страница успешно добавлена', 'success')
            else:
                flash('Страница уже существует', 'info')
            cursor.execute('SELECT id FROM urls WHERE name = %s', (name,))
            id = cursor.fetchone()['id']
            return redirect(url_for('get_site', id=id), code=302)


@app.route('/urls/<id>')
def get_site(id):
    messages = get_flashed_messages(with_categories=True)
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('SELECT * FROM urls WHERE id = %s', (id,))
            site = cursor.fetchone()
    return render_template('show.html', messages=messages, site=site)


@app.route('/urls')
def get_urls():
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('SELECT * FROM urls ORDER BY id DESC')
            sites = cursor.fetchall()
    return render_template('index.html', sites=sites)
