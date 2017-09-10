#!/usr/bin/env python3

from mastodon import Mastodon

from pathlib import Path
from sys import stdout
from os import name

CLIENT = Path('./token.client')
USER = Path('./token.user')
INSTANCE = "https://cybre.space"
NAME = "TootREPL"

# some of this may need to be reworked
def register():
    Mastodon.create_app(NAME, api_base_url = INSTANCE, to_file = CLIENT)

# log us in
def login():
    m = Mastodon(client_id = CLIENT, api_base_url = INSTANCE)

    if not USER.exists():
        email = input("Email> ")
        passwd = input("Password> ")

        m.log_in(email, passwd, to_file = USER)
    
    return Mastodon(client_id = CLIENT, access_token = USER, api_base_url = INSTANCE)

if not CLIENT.exists():
    register()

client = login()

if name == 'posix':
    stdout.write('\33]0;' + NAME + '\a')
else:
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW("TootREPL")

user_in = ['']
last_post = None

print("""Welcome! Type out a status and hit enter to post it!

To quit just type quit

If you want to make a thread, at the end of your status add '|thread'

You can supply a dictionary in the form of 'KEY=VALUE, KEY2=VALUE2, etc'
 but start the string with &

""")
while user_in[0] != "quit":
    user_in = input("Toot> ")

    if user_in.startswith('&'):
        try:
            last_post = client.status_post(**user_in[1:])
        except TypeError:
            print("Whoops, you entered a key that you shouldn't have.\nProper keys are status, visibility, spoiler_text")
    else:
        user_in = user_in.split('|')
        if 'thread' in user_in:
            last_post = client.status_post(user_in[0], in_reply_to_id= last_post)
        elif user_in[0] != 'quit' and user_in[0] != '':
            last_post = client.status_post(user_in[0])
    
    if last_post is not None:
        last_post = last_post['id']
