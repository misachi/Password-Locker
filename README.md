Description
===========================

**Note:** Currently, Locker has been tested and works on linux

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
`pip install -r requirements.txt`.

In the your home directory create a directory, bin, and add it to your path(this applies if you never had the directory before). If you already have the bin directory, just create the file inside it.

Create a bash file e.g your_file_name.sh and copy the code below replacing the path passwords directory, 
in the project root dir, with your path

	#!/bin/bash
	python /path/to/your/project's/directory/Password-Locker/passwords/"$1" "$2"
	
Make your_file_name.sh executable. Run `chown +x your_file_name.sh`. If you get permission denied error, try adding sudo.

Add the bin directory you created to your path(put at the bottom of your .bashrc file)

Now open terminal(Assuming you already have a database setup with the correct config) anywhere and 
run `your_file_name.sh create_relation.py` to create the table

Create a master password - At the command line type `your_file_name.sh dbconnect.py master`. The basic syntax is `your_file_name.sh <script to run> <command>` where command can be any of the following:

|Commannd   |Meaning|
|-----------|--------------------------------|
|master    |create or update master password|
|save_pass  |save account passwords|
|get_pass   |retrieve account password|
|upass   |update account's password|

