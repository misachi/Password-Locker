import os
import sys
import base64
from decouple import config
import pyperclip
from cryptography.fernet import Fernet, MultiFernet

KEY_STORE_DIR = config('KEY_STORE_DIR')


def generate_token(password, key):
    fernet = Fernet(key)
    data = MultiFernet([fernet])
    token = data.encrypt(base64.urlsafe_b64encode(password.encode('utf-8')))
    return token


def verify_password(token):
    with open(os.path.join(KEY_STORE_DIR, 'secrets.txt'), 'rb') as secrets:
        lines = secrets.read()
        all_secrets = [Fernet(b''.join([secret, b'=='])) for secret in
                       lines.split(b'=') if secret != b'']

        #  An attempt to get a key match from list of keys provided
        data = MultiFernet(all_secrets)
        try:
            password = data.decrypt(base64.urlsafe_b64decode(token))
        except:
            print('Token is invalid or does not exist')
            sys.exit()
        raw_passwd = base64.urlsafe_b64decode(password)
        return raw_passwd


def copy_password(account, passw):
    pyperclip.copy(passw)
    print("Password for " + account + " copied to clipboard.")
