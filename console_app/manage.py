from getpass import getpass
import os
import sys
from signal import SIGINT

from core import *
import views

# decorators
def set_up_cml_interface(param_function):
    def inner_function(app, command=None):
        if not command:
            user = app.user
            if not user:
               user = 'anon'
            print(f'[{user}@pompts_club]$ ', end='')
        param_function(app, command)
    return inner_function

# helpers

@set_up_cml_interface
def command(app, command=None):
    if not command: 
        command = input()

    # quick commands, we need to check those 
    # before we split the command; since titles, 
    # tags, etc use spaces.
    if command.startswith('!'):
        scenario_title = command.strip('!')
        views.get_scenario(app, scenario_title)
    elif command.startswith('#'):
        tag = command.strip('#')
        views.get_tagged_scenarios(app, tag)
    elif command.startswith('u'):
        username = input('\nusername: ')
        views.get_user_scenarios(app, username)

    command_and_args = command.split()
    
    command = command_and_args[0]
    try:
        args = command_and_args[1]
    except:
       args = None
  
    if command == 'register':
        usr = input('\nusername: ')
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
        usr = input('\nusername: ')
        psw = getpass('password: ')

        credentials = {
                'username': usr,
                'password': psw
        }
        app.login_user(credentials)
   
    elif command == 'logout':
        app.logout_user()

    elif command == 'get':
        if args.startswith('s'):
            if args.endswith('t'):
                tag = input('\ntag: ')
                views.get_tagged_scenarios(app, tag)
            else:
                views.get_published_scenarios(app)

        elif args.startswith('u'):
            user = input('\nusername: ')
            if args.endswith('s'):
                views.get_user_scenarios(app, user)
            elif args.endswith('f'):
                views.get_user_folders(app, user)
            else:
                views.get_users(app)
        
        elif args.startswith('f'):
            if args.endswith('t'):
                tag = input('\ntag: ')
                views.get_tagged_folders(app, tag)
            elif args.endswith('s'):
                pass
            else:
                views.get_public_folders(app)

    elif command == 'clear':
        os.system('clear')

if __name__ == '__main__':
    app = App()
    while True:
        try:
            command(app)
        except (EOFError, KeyboardInterrupt):
            print('\nbye bye')

            app.session.close()

            sys.exit(SIGINT.value)
