import psycopg2
import bcrypt
import base64
from base64 import b32encode, b32decode
import os
import sys
from psycopg2.extras import execute_values
from getpass import getpass
from cryptography.fernet import Fernet, MultiFernet

# for separating setting parameters from source code
from decouple import config

PARENT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#  I noticed that config from decouple module was misbehaving so I included this
#  workaround just in case. In the 'else' part replace 'passwords' with your database name or a
#  better alternative could be to use os.environ to retrieve environment variables
DATABASE = config('DATABASE') if config('DATABASE') != '' else 'passwords'


def connect_db():
    try:
        # print(DATABASE)
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
    password = getpass('Input the mighty password of all(should be > 8 characters long)...: ')
    if len(password) < 8:
        raise AssertionError('Too short')
    hashed_pass = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    with open(os.path.join(PARENT_DIR, 'master.txt'), 'wb') as pass_file:
        pass_file.write(hashed_pass)


def login():
    password = getpass('Input password: ')
    try:
        with open(os.path.join(PARENT_DIR, 'master.txt'), 'rb') as pass_file:
            hashed = pass_file.read()
            if bcrypt.checkpw(password.encode('utf-8'), hashed):
                print('Password confirmed')
                return True
    except (IOError, EOFError):
        print('Wrong password')


def save_account_passwords():
    choice = True
    conn = connect_db()
    cur = conn.cursor()
    if login() is True:
        result = []

        with open(os.path.join(PARENT_DIR, 'secrets.txt'), 'ab') as secret:
            while choice:
                account_name = input('Account name: ')
                password = getpass('Account"s password: ')
                key = Fernet.generate_key()
                fernet = Fernet(key)

                data = MultiFernet([fernet])
                token = data.encrypt(base64.urlsafe_b64encode(password.encode('utf-8')))

                # data = MultiFernet([fernet])
                # password = data.decrypt(token)
                # print(token)
                # print(base64.urlsafe_b64decode(password))

                #  Here the password is decoded once again to ensure it is not
                #  wrongfully encoded by the database encoder (I learnt this the painful way)
                result.append((account_name, base64.urlsafe_b64encode(token)))
                # secret.write('{0} {1}'.format(account_name, key).strip(' '))
                secret.write(key)
                quiz = input('Still more? ("Yes" to add more or "No" to quit): ').lower()

                if quiz in ['yes', 'no']:
                    if quiz == 'no':
                        choice = False
                else:
                    raise KeyError('Choices are "Yes" and "No"!')
        query = '''INSERT INTO vault (account, password) VALUES %s'''
        execute_values(cur, query, result)
        conn.commit()
        conn.close()
    else:
        conn.close()
        raise PermissionError('Unauthorized user')


def retrieve_password():
    conn = connect_db()
    cur = conn.cursor()
    if login() is True:
        account_name = input('Please enter account to retrieve password...: ')
        try:
            query = cur.mogrify('''SELECT * FROM vault WHERE account = %s''', (account_name, ))
            cur.execute(query, account_name)
            return_row = cur.fetchone()
            with open(os.path.join(PARENT_DIR, 'secrets.txt'), 'rb') as secrets:
                lines = secrets.read()
                all_secrets = [Fernet(b''.join([secret, b'=='])) for secret in lines.split(b'=') if secret != b'']

                #  An attempt to get a key match from list of keys provided
                data = MultiFernet(all_secrets)

                password = data.decrypt(base64.urlsafe_b64decode(return_row[2]))
                raw_passwd = base64.urlsafe_b64decode(password)
                return raw_passwd
        except LookupError:
            print('account matching query does not exist')
    else:
        raise PermissionError('Unauthorized user')

# save_master_password()
# save_account_passwords()
retrieve_password()
