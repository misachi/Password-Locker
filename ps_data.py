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
        SELECT * FROM user_password_data
    ''')
    foo = cur.fetchall()

    PASSWORDS = dict(outlook=foo[0][2], gmail=foo[1][2], twitter=foo[2][2], facebook=foo[3][2], freelancer=foo[4][2],
                     bitlocker=foo[5][2], MMU=foo[6][2], mysql=foo[7][2], user_brayo=foo[8][2], firefox=foo[9][2],
                     dropbox=foo[10][2], wp_tuts_pwd=foo[11][2], wp_tuts_usr=foo[12][2])

except ConnectionError:
    print("Unable to connect")


