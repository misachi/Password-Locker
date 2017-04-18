#! python3


import sys, pyperclip, ps_data

if len(sys.argv) < 2:
    print("Please provide an account name...")
    sys.exit()

account = sys.argv[1]  # first command line arg is the account name

if account in ps_data.PASSWORDS:
    pyperclip.copy(ps_data.PASSWORDS[account])
    print("Password for " + account + "copied to clipboard.")
else:
    # if account not found
    print("There is no account named " + account)
