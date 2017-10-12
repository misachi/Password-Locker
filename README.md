Description
===========================

**Note:** Currently, Locker has been tested and works on Ubuntu and Mac

Locker is a commandline utility program that helps users store their passwords.It eliminates the need for crumming or having to remember all of your passwords. It has the ability to persist the desired encrypted secret/password in a database and retrieve it later
for use.Locker allows storage of multiple account passwords at once

Basic Requirements
===========================
Basic requirements for Locker to run are:

	- Python v2.7, v3.5
	- Postgresql 9.6.x and above
	- User with read/write permissions

How it works (install)
===========================

Locker is a python program, that means it can run on most platforms,although, only linux platform has been tested.It uses the cryptography package to encrypt and decrypt the password before and after storage.The generated key is stored in a separate location(pickled file or plain text file) - Your choice.It is up to the user to choose where these files are stored in their system.Just ensure you have the required read & write permissions to the folders/locations you choose.Here is a walk through of how to run it anywhere in your system.

To begin `Clone <https://github.com/misachi/Password-Locker.git>`_ to a directory of choice and run 
`pip install -r /path/to/project/requirements.txt`.

In the your home directory create a directory, bin, and add it to your path(this applies if you never had the directory before). If you already have the bin directory, just create the file inside it.

Create a bash file e.g your_file_name.sh and copy the code below replacing the path passwords directory, 
in the project root dir, with your path. Or you could write your own bash script to perform the same.

	#!/bin/bash

	MAIN_PASS_DIR=/path/to/your/location(folder)/to/keep/master password
	KEY_STORE_DIR=/path/to/your/loaction/to/store/account passwords

	DIR_NAME=/path/to/location/of cloned/project  # this should be like /path/Password-Locker/password

	if [ ! -d  "$MAIN_PASS_DIR" ]
	then
		mkdir $MAIN_PASS_DIR && touch "${MAIN_PASS_DIR}/master.txt"
	fi

	if [ ! -d "$KEY_STORE_DIR" ]; then
		mkdir $KEY_STORE_DIR && touch "${KEY_STORE_DIR}/account_keys.txt"
	fi

	if [[ "$1" == 'table' ]]; then
		python "${DIR_NAME}/create_relation.py"
	elif [[ "$1" == 'save_pass' ]]; then
		python "${DIR_NAME}/dbconnect.py" "$1"
	elif [[ "$1" == 'master' ]]; then
		python "${DIR_NAME}/dbconnect.py" "$1"
	elif [[ "$1" == 'get_pass' ]]; then
		python "${DIR_NAME}/dbconnect.py" "$1"
	elif [[ "$1" == 'upass' ]]; then
		python "${DIR_NAME}/dbconnect.py" "$1"
	else
		python "${DIR_NAME}/dbconnect.py" "$1"
	fi

	exit $?
	
You can also create a symlink to your bash script

	ln -s path/to/your_file_name.sh path/to/sym_link
	
**NOTE** This is not a requirement
	
Make your_file_name.sh executable. Run `chown +x /your/path/to/your_file_name.sh`. If you get permission denied error, try adding sudo.

Add the bin directory you created to your path(put at the bottom of your .bashrc file)

Now open terminal(Assuming you already have a database setup with the correct configurations) anywhere and 
run `your_file_name.sh table` to create the table

Create a master password - At the command line type `your_file_name.sh or sym_link master`. The basic syntax is `<your_file_name.sh> <command> or <sym_link> <command>` where command can be any of the following:

|Commannd   |Meaning|
|-----------|--------------------------------|
|table|create table if its your first time using locker|
|master    |create or update master password|
|save_pass  |save account passwords|
|get_pass   |retrieve account password|
|upass   |update account's password|


Rename the .env_example file to .env and replace the config data accordingly. `MAIN_PASS_DIR describes the directory to store your master password(hashed of course).` Ensure you have read/write access to this directory. `KEY_STORE_DIR describes the directory you'd want to store the file containing your encryption keys`. As before, ensure you have read/write access to this directory.

Enjoy :)

