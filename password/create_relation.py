from dbconnect import connect_db


def create_table():
    conn = connect_db()
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE vault(
            id          SERIAL      PRIMARY KEY,
            account     CHAR(20)    NOT NULL,
            password    BYTEA       NOT NULL
        )
    ''')

    print("Table created successfully")

    conn.commit()

create_table()
