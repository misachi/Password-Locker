import psycopg2
from decouple import config  # for separating setting
# parameters from source code


def connect_db():  # function attempts to make a connection
    try:  # with the database and returns a connection object if successful
        conn = psycopg2.connect(
            database=config("DATABASE"),
            user=config("USER"),
            password=config("PASSWORD"),
            host=config("HOST"),
            port=config("PORT")
        )

        return conn
    except ConnectionError:
        print("Unable to connect")
