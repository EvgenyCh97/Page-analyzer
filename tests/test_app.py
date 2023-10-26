import os

import psycopg2
import psycopg2.extras
import pytest
from dotenv import load_dotenv
from playwright.sync_api import Page, expect

import page_analyzer

load_dotenv()
URL = os.getenv('DEV_URL', 'http://server:8001')
DATABASE_URL = os.getenv('DATABASE_URL')


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


def test_get_main_page(client):
    response = client.get('/')
    assert response.status_code == 200


def test_check_url(page: Page):
    try:
        page.goto(f'{URL}/')
        page.get_by_placeholder("https://www.example.com"). \
            fill("")
        page.locator('input[type="submit"]').click()
        expect(page.get_by_text("URL обязателен")).to_be_visible()

        page.get_by_placeholder("https://www.example.com"). \
            fill("test@")
        page.locator('input[type="submit"]').click()
        expect(page.get_by_text("Некорректный URL")).to_be_visible()

        page.goto(f'{URL}/')
        page.get_by_placeholder("https://www.example.com"). \
            fill("https://test.com")
        page.locator('input[type="submit"]').click()
        expect(page.get_by_text("Страница успешно добавлена")).to_be_visible()

        page.goto(f'{URL}/')
        page.get_by_placeholder("https://www.example.com"). \
            fill("https://TEST.com")
        page.locator('input[type="submit"]').click()
        expect(page.get_by_text("Страница уже существует")).to_be_visible()

    finally:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('DELETE FROM urls WHERE name = %s',
                               ('https://test.com',))


def test_get_urls(page: Page):
    page.goto(f'{URL}/urls')
    expect(page.get_by_role("heading", name="Сайты")).to_be_visible()
    expect(page.get_by_role("table", name='')).to_be_visible()


def test_run_check(page: Page):
    try:
        page.goto(f'{URL}/')
        page.get_by_placeholder("https://www.example.com"). \
            fill("https://aaa.ru")
        page.locator('input[type="submit"]').click()
        page.locator('text=Запустить проверку').click()
        expect(page.get_by_text("Страница успешно проверена")).to_be_visible()

        page.goto(f'{URL}/')
        page.get_by_placeholder("https://www.example.com"). \
            fill("https://ccc.com")
        page.locator('input[type="submit"]').click()
        page.locator('text=Запустить проверку').click()
        expect(
            page.get_by_text("Произошла ошибка при проверке")).to_be_visible()

    finally:
        with psycopg2.connect(DATABASE_URL) as connection:
            with connection.cursor(
                    cursor_factory=psycopg2.extras.DictCursor) as cursor:
                cursor.execute('DELETE FROM urls WHERE name = %s',
                               ('https://aaa.ru',))
                cursor.execute('DELETE FROM urls WHERE name = %s',
                               ('https://ccc.com',))
