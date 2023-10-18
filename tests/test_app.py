import datetime

import psycopg2
import psycopg2.extras
import pytest
from playwright.sync_api import Page, expect

import page_analyzer
from page_analyzer.database_handlers import (DATABASE_URL, insert_into_db,
                                             select_from_db)


@pytest.fixture()
def app():
    app = page_analyzer.app
    app.config.update({
        "ENV": 'testing',
        "TESTING": True,
    })
    yield app


@pytest.fixture()
def client(app):
    return app.test_client()


def test_select_from_db():
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('INSERT INTO urls (name, created_at) '
                           'VALUES (%s, %s)', ('test_select', '2023-10-18'))
            connection.commit()
            result = select_from_db(
                'SELECT name, created_at FROM urls WHERE name = %s',
                ('test_select',))
            assert result == [['test_select', datetime.date(
                2023, 10, 18)]]
            cursor.execute('DELETE FROM urls WHERE name = %s',
                           ('test_select',))
            connection.commit()


def test_insert_into_db():
    insert_into_db('INSERT INTO urls (name, created_at) VALUES (%s, %s)',
                   ('test_insert', '2023-10-18'))
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('SELECT name, created_at FROM urls WHERE name = %s',
                           ('test_insert',))
            assert cursor.fetchone() == ['test_insert', datetime.date(
                2023, 10, 18)]
            cursor.execute('DELETE FROM urls WHERE name = %s',
                           ('test_insert',))
            connection.commit()


def test_get_main_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_check_site(page: Page):
    page.goto('http://127.0.0.0:8001/')
    page.get_by_placeholder("https://www.example.com"). \
        fill("")
    page.locator('input[type="submit"]').click()
    expect(page.get_by_text("URL обязателен")).to_be_visible()

    page.get_by_placeholder("https://www.example.com"). \
        fill("test@")
    page.locator('input[type="submit"]').click()
    expect(page.get_by_text("Некорректный URL")).to_be_visible()

    page.goto('http://127.0.0.0:8001/')
    page.get_by_placeholder("https://www.example.com"). \
        fill("https://test.com")
    page.locator('input[type="submit"]').click()
    expect(page.get_by_text("Страница успешно добавлена")).to_be_visible()

    page.goto('http://127.0.0.0:8001/')
    page.get_by_placeholder("https://www.example.com"). \
        fill("https://TEST.com")
    page.locator('input[type="submit"]').click()
    expect(page.get_by_text("Страница уже существует")).to_be_visible()

    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('DELETE FROM urls WHERE name = %s',
                           ('https://test.com',))


def test_get_urls(page: Page):
    page.goto('http://127.0.0.0:8001/urls')
    expect(page.get_by_role("heading", name="Сайты")).to_be_visible()
    expect(page.get_by_role("table", name='')).to_be_visible()


def test_get_check(page: Page):
    page.goto('http://127.0.0.0:8001/')
    page.get_by_placeholder("https://www.example.com"). \
        fill("https://aaa.ru")
    page.locator('input[type="submit"]').click()
    page.locator('text=Запустить проверку').click()
    expect(page.get_by_text("Страница успешно проверена")).to_be_visible()

    page.goto('http://127.0.0.0:8001/')
    page.get_by_placeholder("https://www.example.com"). \
        fill("https://ccc.com")
    page.locator('input[type="submit"]').click()
    page.locator('text=Запустить проверку').click()
    expect(page.get_by_text("Произошла ошибка при проверке")).to_be_visible()

    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute('DELETE FROM urls WHERE name = %s',
                           ('https://aaa.ru',))
            cursor.execute('DELETE FROM urls WHERE name = %s',
                           ('https://ccc.com',))
