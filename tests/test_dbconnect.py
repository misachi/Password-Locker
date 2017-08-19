import pytest
from password.dbconnect import connect_db


class TestDBConnect:
    def test_connect_db(self):
        foo = connect_db()


