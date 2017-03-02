import psycopg2

try:
    conn = psycopg2.connect(
        database="passwords",
        user="user",
        password="pword",
        host="127.0.0.1",
        port="5432"
    )
    cur = conn.cursor()

    cur.execute('''
        CREATE TABLE user_password_data (
            ID          INT         PRIMARY KEY     NOT NULL,
            ACCOUNT     CHAR(20)    NOT NULL,
            PASSWORD    CHAR(100)   NOT NULL
        )
    ''')

    print("Table created successfully")

    conn.commit()
except ConnectionError:
    print("A connection error occurred")