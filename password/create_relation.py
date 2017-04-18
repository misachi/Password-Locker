from dbconnect import connect_db

conn = connect_db()
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
