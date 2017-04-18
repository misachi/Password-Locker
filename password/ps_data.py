from dbconnect import connect_db

conn = connect_db()
cur = conn.cursor()
cur.execute('''
    SELECT * FROM user_password_data
''')
db_data = cur.fetchall()  # fetch the list data from database

PASSWORDS = dict(
    outlook=db_data[0][2],
    gmail=db_data[1][2],
    twitter=db_data[2][2]
)
