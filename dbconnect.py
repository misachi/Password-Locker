import psycopg2


def connect_db():  # function attempts to make a connection with the database
    try:  # and returns a connection object if successful
        conn = psycopg2.connect(
            database="passwords",
            user="user",
            password="pword",
            host="127.0.0.1",
            port="5432"
        )

        return conn
    except ConnectionError:
        print("Unable to connect")
