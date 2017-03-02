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
        INSERT INTO user_password_data VALUES (1, 'ol', 'abcd')
    ''')
    cur.execute('''
        INSERT INTO user_password_data VALUES (2, 'gmail', 'efgh')
    ''')
    cur.execute('''
        INSERT INTO user_password_data VALUES (3, 'twitter', 'ijkl')
    ''')
    cur.execute('''
        INSERT INTO user_password_data VALUES (4, 'fb', 'mnop')
    ''')
    print("Values inserted successfully")
    conn.commit()
except ConnectionError:
    print("Unable to connect")

