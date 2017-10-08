import psycopg2
import bcrypt
import base64
import os
import sys
from getpass import getpass
from cryptography.fernet import Fernet
from decouple import config
from psycopg2.extras import execute_values

from utils import verify_password, generate_token
from pythonScript import copy_password

# To do run cronjob to remind user to change master password after 3 days

MAIN_PASS_DIR = config('MAIN_PASS_DIR')
KEY_STORE_DIR = config('KEY_STORE_DIR')

"""
Am doing this on the bash script due to permission issue when done using python
"""
# if not os.path.exists(MAIN_PASS_DIR):
#     os.makedirs(MAIN_PASS_DIR)
#
# if not os.path.exists(KEY_STORE_DIR):
#     os.makedirs(KEY_STORE_DIR)


#  I noticed that config from decouple module was misbehaving so I included
# this workaround just in case. In the 'else' part replace 'passwords' with
# your database name or a better alternative could be to use os.environ to
# retrieve environment variables
DATABASE = config('DATABASE') if config('DATABASE') != '' else 'passwords'


def connect_db():
    try:
        conn = psycopg2.connect(
            database=DATABASE,
            user=config('DATABASE_USER'),
            password=config('DATABASE_PASSWORD'),
            host=config('HOST'),
            port=config('PORT')
        )

        return conn
    except (ConnectionError, ConnectionRefusedError):
        print('Unable to connect')


def save_master_password():
    path = os.path.join(MAIN_PASS_DIR, 'master.txt')
    if os.path.exists(path):
        quiz = input('Do you want to replace  master password(Yes or No)? ')
        low_er = quiz.lower()
        if low_er in ['yes', 'y', 'no', 'n']:
            if low_er == 'no' or low_er == 'n':
                sys.exit()
        else:
            print('Choices can only be Yes, No, Y, N, n, y')
            sys.exit()

    password = getpass(
        'Input the mighty password of all(should be > 8 characters long)...: ')

    if len(password) < 8:
        raise AssertionError(
            'Too short(password should be at least 8 characters long)')
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

    with open(path, 'wb') as pass_file:
        pass_file.write(hashed_pass)


def login():
    password = getpass('Input password: ')
    with open(os.path.join(MAIN_PASS_DIR, 'master.txt'), 'rb') as pass_file:
        hashed = pass_file.read()
        if bcrypt.checkpw(password.encode('utf-8'), hashed):
            print('Password confirmed')
            return True


def save_account_passwords(conn):
    choice = True
    cur = conn.cursor()

    result = []
    with open(os.path.join(KEY_STORE_DIR, 'secrets.txt'), 'ab') as secret:
        while choice:
            account_name = input('Account name: ')
            password = getpass('Account"s password: ')
            key = Fernet.generate_key()
            token = generate_token(password, key)

            #  Here the password is decoded once again to ensure it is not
            #  'wrongfully' encoded by the database encoder (I learnt this the
            #  painful way)
            result.append((account_name, base64.urlsafe_b64encode(token)))
            secret.write(key)
            quiz = input(
                    'Still more? ("Yes" to add more or "No" to quit): '
                    ).lower()

            if quiz in ['yes', 'y', 'no', 'n']:
                if quiz == 'no' or quiz == 'n':
                    choice = False
            else:
                print('Choices are "Yes" and "No"!')
                break
    query = '''INSERT INTO vault (account, password) VALUES %s'''
    execute_values(cur, query, result)
    conn.commit()
    cur.close()


def retrieve_password(conn):
    cur = conn.cursor()

    account_name = input('Please enter account to retrieve password...: ')

    try:
        query = cur.mogrify('''SELECT * FROM vault WHERE account = %s''',
                            (account_name, ))
        cur.execute(query, account_name)
        return_row = cur.fetchone()
        raw_passwd = verify_password(return_row[2])
        cur.close()
        return account_name, raw_passwd.decode('utf-8')
    except LookupError:
        print('account matching query does not exist')
        sys.exit()


def update_password(conn):
    cur = conn.cursor()

    account = input('Account name to be changed: ')
    try:
        query = cur.mogrify('''SELECT * FROM vault WHERE account = %s''',
                            (account, ))
        cur.execute(query, account)
        return_row = cur.fetchone()
        raw_passwd = verify_password(return_row[2])
        print(raw_passwd)
        chance = 0
        while chance <= 2:
            old_password = getpass('Old password: ')
            print(old_password)
            if raw_passwd.decode('utf-8') != old_password:
                print('Incorrect password!')
                if chance == 2:
                    print('You have tried the wrong password 3 times!')
                    sys.exit()
            else:
                break
            chance += 1
    except LookupError:
        print('account matching query does not exist')
        sys.exit()

    key = Fernet.generate_key()
    new_password = getpass('New password')
    token = generate_token(new_password, key)
    with open(os.path.join(KEY_STORE_DIR, 'secrets.txt'), 'ab') as secret:
        secret.write(key)
    args = (base64.urlsafe_b64encode(token), account)
    query = cur.mogrify('''UPDATE vault SET password = %s
    WHERE account = %s''', args)
    cur.execute(query)
    conn.commit()
    cur.close()


if __name__ == '__main__':
    arg_list = ['master', 'save_pass', 'get_pass', 'upass']
    if len(sys.argv) < 2 or sys.argv[1] is '':
        raise Exception('Please provide a command')

    if sys.argv[1] not in arg_list:
        raise IndexError('Wrong index value')

    if sys.argv[1] == arg_list[0]:
        save_master_password()
    else:
        if not login():
            raise PermissionError('Unauthorized user')

        conn = connect_db()
        if sys.argv[1] == arg_list[1]:
            save_account_passwords(conn)
        elif sys.argv[1] == arg_list[2]:
            account, passw = retrieve_password(conn)
            copy_password(account, passw)
        elif sys.argv[1] == arg_list[3]:
            update_password(conn)
        conn.close()
