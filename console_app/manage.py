from getpass import getpass
import os
import sys
from signal import SIGINT

from core import *
from utils import get_user_scenarios

# decorators
def set_up_cml_interface(param_function):
    def inner_function(app):
        user = app.user
        if not user:
           user = 'anon'
        print(f'[{user}@pompts_club]$ ', end='')
        param_function(app)
    return inner_function

# helpers
def get_command_with_args():
    try:
        command = input()
    except (EOFError, KeyboardInterrupt):
        print('\nbye bye')
        sys.exit(SIGINT.value)
    command_and_args = command.split()
    
    command = command_and_args[0]
    
    args = [arg for arg in command_and_args]
    args.pop(0)
    
    return {
            'command': command,
            'args': args
           }    

@set_up_cml_interface
def command(app):
    command_and_args = get_command_with_args()

    command = command_and_args['command']
    args = command_and_args['args']
    
    if command == 'register':
        usr = input('username: ')
        psw1 = getpass('password: ')
        psw2 = getpass('password(again): ')
        
        if psw1 == psw2:
            credentials = {
                    'username': usr,
                    'password': psw1
            }
            app.create_user(credentials)

        else:
            print('Passwords did not match.')

    elif command == 'login':
        usr = input('username: ')
        psw = getpass('password: ')

        credentials = {
                'username': usr,
                'password': psw
        }
        app.login_user(credentials)
   
    elif command == 'logout':
        app.logout_user()

    elif command == 'get':
        try:
            if args[0] == 'user':
                if args[1] == 'scenarios':
                    user = input('username: ')
                    get_user_scenarios(app, user)
        except KeyError:
            print('\nbad command')

    elif command == 'clear':
        os.system('clear')

if __name__ == '__main__':
    app = App()
    while True:
        command(app)
