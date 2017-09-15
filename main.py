#!/usr/bin/env python3

from mastodon import Mastodon

from pathlib import Path
from sys import stdout
from os import name
from configparser import ConfigParser
import readline

conf = ConfigParser()

CONF_FILE = Path("./config.ini")
INSTANCE = "https://mastodon.social"
NAME = "TootREPL"

CMDS = [ '!emacs', '!vi', '!quit', '!q', '!help' ]
MODE_CMDS = CMDS[:2]

INTRO = """Welcome! Type out a status and hit enter to post it!

To quit just type !quit

If you want to make a thread, at the beginning of your status add '!thread'

You can supply a dictionary in the form of 'KEY=VALUE, KEY2=VALUE2, etc'
 but start the string with !dict

"""



# updates readline mode
def change_readline_mode(newMode):
    newMode = newMode[1:]
    if newMode in [ 'emacs', 'vi' ]:
        readline.parse_and_bind('set editing-mode ' + newMode)


# saves the config file again
def update_conf():
    with open(CONF_FILE, 'w') as f:
        conf.write(f)


# register the app if we don't see any client tokens
def register():
    conf['default']['client_id'], conf['default']['client_secret'] = Mastodon.create_app(NAME, api_base_url = conf['default']['instance'])
    update_conf()


# log us in
def login():
    if not 'access' in conf['default'].keys():
        print("Since I don't see any tokens we'll have to log in",
              "\n",
              "*your email and password are not saved and only used to get auth tokens*")
        email = input("Email> ")
        passwd = input("Password> ")

        m = Mastodon(client_id = conf['default']['client_id'],
                     client_secret = conf['default']['client_secret'],
                     api_base_url = conf['default']['instance'])
        conf['default']['access'] = m.log_in(email, passwd)
        del m
        update_conf()
    
    return Mastodon(client_id = conf['default']['client_id'],
                    client_secret = conf['default']['client_secret'],
                    access_token = conf['default']['access'],
                    api_base_url = conf['default']['instance'])

###

# changes the window name
if name == 'posix':
    stdout.write('\33]0;' + NAME + '\a')
else: # for windows
    import ctypes
    ctypes.windll.kernel32.SetConsoleTitleW("TootREPL")

# initializes the config to something so it won't bitch on first run
conf['default'] = {}


# if we have a config file, we parse it
#  otherwise we start a new one
if CONF_FILE.exists():
    conf.read(CONF_FILE)
else:
    inst = input("Instance (Default: mastodon.social)> ")
    if inst != '':
        if not inst.startswith("https://") or \
           not inst.startswith("http://"):
            inst = "https://" + inst
        INSTANCE = inst
        
    conf['default']['instance'] = INSTANCE

if not 'client_id' in conf['default'].keys():
    register()

client = login()
user_in = ''
last_post = None

print(INTRO)
while user_in not in ['!quit', '!q']:
    user_in = input("Toot> ")

    if user_in.split()[0] not in CMDS:
        if user_in.startswith('!dict'):
            try:
                ## converts the string into a dict
                user_in = dict( (k.strip(), v.strip()) for k,v in (j.split('=') for j in user_in[6:].split(',') ) )
                last_post = client.status_post(**user_in)
            except TypeError:
                print("Whoops, you entered a key that you shouldn't have.\nProper keys are status, visibility, spoiler_text")
        else:
            if user_in.startswith('!thread'):
                last_post = client.status_post(user_in[8:], in_reply_to_id= last_post)
            elif user_in != '':
                last_post = client.status_post(user_in)
            else:
                last_post = None
    else:
        if user_in in MODE_CMDS:
            change_readline_mode(user_in)
        if user_in == '!help':
            print(INTRO)
    
    if last_post is not None:
        last_post = last_post['id']
