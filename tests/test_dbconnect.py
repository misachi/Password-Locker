import pytest
import psycopg2
from psycopg2.extras import execute_values
import testing.postgresql
import base64
import unittest

# from password.dbconnect import connect_db


def handler(postgresql):
    conn = psycopg2.connect(**postgresql.dsn())
    cursor = conn.cursor()
    cursor.execute('''
            CREATE TABLE vault(
                id          SERIAL      PRIMARY KEY,
                account     CHAR(20)    NOT NULL,
                password    BYTEA        NOT NULL
            )
    ''')
    query = '''INSERT INTO vault (account, password) VALUES %s'''
    data = [('twitter', b'pass'), ('fb', b'fb')]
    execute_values(cursor, query, data)
    cursor.close()
    conn.commit()
    conn.close()


Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True,
                                                  on_initialized=handler)


class TestDBConnect(unittest.TestCase):
    def setUp(self):
        # Use the generated Postgresql class instead of testing.postgresql.Postgresql
        self.postgresql = Postgresql()

    def test_connect_db(self):
        assert True

    def tearDown(self):
        self.postgresql.stop()


