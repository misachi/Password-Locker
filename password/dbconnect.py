import psycopg2
import bcrypt
import base64
import os
import sys
from getpass import getpass
from cryptography.fernet import Fernet, MultiFernet
from decouple import config
from psycopg2.extras import execute_values
import logging

from utils import verify_password, generate_token, copy_password

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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

handler = logging.FileHandler('locker.logs')
handler.setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
handler.setFormatter(formatter)

logger.addHandler(handler)
#  I noticed that config from decouple module was misbehaving so I included
# this workaround just in case. In the 'else' part replace 'passwords' with
# your database name or a better alternative could be to use os.environ to
# retrieve environment variables
DATABASE = config('DATABASE') if config('DATABASE') != '' else 'passwords'
if sys.version.split('.')[0] <= 2:
    """
    Python 2 has no global names PermissionError, ConnectionError 
    or ConnectionRefusedError hence this
    """
    class PermissionError(Exception):
        pass


    class ConnectionError(Exception):
        pass


    class ConnectionRefusedError(Exception):
        pass


def connect_db():
    try:
        conn = psycopg2.connect(
            database=DATABASE,
            user=config('DATABASE_USER'),
            password=config('DATABASE_PASSWORD'),
            host=config('HOST'),
            port=config('PORT')
        )
        logger.info('Database connection successful')
        return conn
    except (ConnectionError, ConnectionRefusedError):
        logger.exception('Connection Error')
        print('Unable to connect')


def save_master_password():
    path = os.path.join(MAIN_PASS_DIR, 'master.txt')
    if os.path.exists(path):
        quiz = input('Do you want to replace  master password(Yes or No)? ')
        low_er = quiz.lower()
        if low_er in ['yes', 'y', 'no', 'n']:
            if low_er == 'no' or low_er == 'n':
                logger.info('User chose not to alter master password')
                sys.exit()
        else:
            logger.warning('Appropriate answer not provided')
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
    print(login)
    print(MAIN_PASS_DIR)
    with open(os.path.join(MAIN_PASS_DIR, 'master.txt'), 'rb') as pass_file:
        hashed = pass_file.read()
        try:
            if bcrypt.checkpw(password.encode('utf-8'), hashed):
                logger.info('Master Login was successful')
                print('Password confirmed')
                return True
        except:
            logger.critical('Master login unsuccessful')
            return False


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
                    logger.info('User chose not to add more accounts')
                    choice = False
            else:
                print('Choices are "Yes" and "No"!')
                logger.warning('Wrong/Unrecognized choice made by user')
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
        logger.info('Password decryption successful')
        cur.close()
        return account_name, raw_passwd.decode('utf-8')
    except LookupError:
        logger.exception('Lookup error on database, account provided by user not in database')
        print('account matching query does not exist')
        sys.exit()

# 
# def delete_password(conn):
#     cur = conn.cursor()

#     account = input('Please input account to delete: ')
#     # try:
#     query = cur.mogrify('''SELECT * FROM vault WHERE account = %s''',
#                         (account, ))
#     cur.execute(query, account)
#     return_row = cur.fetchone()
#     with open(os.path.join(KEY_STORE_DIR, 'secrets.txt'), 'rb') as secrets:
#         lines = secrets.read()
#         all_secrets = [Fernet(b''.join([secret, b'=='])) for secret in
#                     lines.split(b'=') if secret != b'']
#         # print(all_secrets)

#         #  An attempt to get a key match from list of keys provided
#         data = MultiFernet(all_secrets)
#         print(data)
#         # del(data)
#         # print('hooray')

#             # try:
#             #     password = data.decrypt(base64.urlsafe_b64decode(token))
#             # except:
#             #     print('Token is invalid or does not exist')
#             #     sys.exit()
#             # raw_passwd = base64.urlsafe_b64decode(password)
#             # return raw_passwd

#         # query = cur.mogrify('''DELETE * FROM vault WHERE account = %s''', (account, ))
#         # cur.execute(query)
#     # except:
#     #     pass        


def update_password(conn):
    cur = conn.cursor()

    account = input('Account name to be changed: ')
    try:
        query = cur.mogrify('''SELECT * FROM vault WHERE account = %s''',
                            (account, ))
        cur.execute(query, account)
        return_row = cur.fetchone()
        raw_passwd = verify_password(return_row[2])
        chance = 0
        while chance <= 2:
            old_password = getpass('Old password: ')
            if raw_passwd.decode('utf-8') != old_password:
                logger.warning('Password given by user does not match existing password in database')
                print('Incorrect password!')
                if chance == 2:
                    print('You have tried the wrong password 3 times!')
                    logger.fatal('User entered incorrect password 3 times')
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
    commands = '''
    Here are the command to use with locker:\n
    1. master - Create or alter master password\n
    2. save_pass - Add new account to save password\n
    3. get_pass - Retrieve password for an account\n
    4. upass - Update/Change password for account\n
    Example usage: locker upass\n
    '''
    logger.info('Successful on start...')
    print(commands)
    arg_list = ['master', 'save_pass', 'get_pass', 'upass']
    if len(sys.argv) < 2 or sys.argv[1] is '':
        logger.fatal('No command provided by user')
        raise Exception('Please provide a command')

    if sys.argv[1] not in arg_list:
        logger.fatal('User provided command not in allowed commands(Unrecognized command %s)' % sys.argv[1])
        raise IndexError('Wrong index value')

    if sys.argv[1] == arg_list[0]:
        logger.info('User chose to alter master password')
        save_master_password()
    else:
        if not login():
            logger.critical('Wrong password submitted by user')
            raise PermissionError('Unauthorized user')

        conn = connect_db()
        if sys.argv[1] == arg_list[1]:
            logger.info('User chose to add a new account')
            save_account_passwords(conn)
        elif sys.argv[1] == arg_list[2]:
            logger.info('User chose to retrieve their account password')
            account, passw = retrieve_password(conn)
            copy_password(account, passw)
        elif sys.argv[1] == arg_list[3]:
            logger.info('User chose to update password')
            update_password(conn)
        conn.close()
    logger.info('Succesful on END...')
