import os

import psycopg2
import psycopg2.extras
from dotenv import load_dotenv

load_dotenv()
DATABASE_URL = os.getenv('DATABASE_URL')


def insert_into_db(query, values):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, (*values,))
            connection.commit()


def select_from_db(query, values=()):
    with psycopg2.connect(DATABASE_URL) as connection:
        with connection.cursor(
                cursor_factory=psycopg2.extras.DictCursor) as cursor:
            cursor.execute(query, (*values,))
            return cursor.fetchall()
