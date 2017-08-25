import pyperclip


def copy_password(account, passw):
    pyperclip.copy(passw)
    print("Password for " + account + " copied to clipboard.")

