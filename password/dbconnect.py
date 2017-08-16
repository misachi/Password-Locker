import psycopg2
from getpass import getpass
import bcrypt
import os
import sys

# for separating setting parameters from source code
from decouple import config

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


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


def save_master_password():
    password = getpass('Input the mighty password of all(should be > 8 characters long)...: ')
    if len(password) < 8:
        raise AssertionError('Too short')
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with open(os.path.join(PARENT_DIR, 'ps.txt'), 'wb') as pass_file:
        pass_file.write(hashed_pass)


def login():
    password = getpass('Input password: ')
    with open(os.path.join(PARENT_DIR, 'ps.txt'), 'rb') as pass_file:
        hashed = pass_file.read()
        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            print('Password confirmed')
            return True


def save_account_passwords():
    choice = True
    conn = connect_db()
    cur = conn.cursor()
    if login() is True:
        result = []
        while choice:
            account_name = input('Account name: ')
            password = getpass('Account"s password: ')
            hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

            cur.execute(
                '''INSERT INTO vault (account, password) VALUES ({0} {1})'''.format(account_name, hashed)
            )

            quiz = input('Still more? ("Yes" to add more or "No" to quit): ')
            if quiz.lower() == 'no':
                choice = False
        cur.batchexecute()
        conn.commit()
    else:
        raise PermissionError('Unauthorized user')







