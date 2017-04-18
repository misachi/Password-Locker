from dbconnect import connect_db

conn = connect_db()
cur = conn.cursor()

# Populating database with arbitrary data
cur.execute('''
    INSERT INTO user_password_data VALUES (1, 'ol', 'abcd')
''')
cur.execute('''
    INSERT INTO user_password_data VALUES (2, 'gmail', 'efgh')
''')
cur.execute('''
    INSERT INTO user_password_data VALUES (3, 'twitter', 'ijkl')
''')

print("Values inserted successfully")
conn.commit()
