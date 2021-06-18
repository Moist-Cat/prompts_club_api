from getpass import getpass
import os
import sys
from signal import SIGINT

from core import *
import views
from help import *

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

    # Need to check quick commands before the split 
    # since some scenarios have spaces
    if command.startswith('!'):
        scenario_title = command.strip('!')
        views.view_scenario(app, scenario_title)
    elif command.startswith('#'):
        tag = command.strip('#')
        views.view_tagged_scenarios(app, tag)
    elif command.startswith('u'):
        username = input('\nusername: ')
        views.view_user_scenarios(app, username)


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
    
    elif command == 'clear':
        os.system('clear')
    
    # from here, all the commands need args 
    # so we return if there are none
    elif not args:
        print('Command not recognized...')
        return
    
    elif command == 'mine':
         if args.startswith('s'):
            if args.endswith('t'):
                tag = input('\ntag:')
                views.view_my_tagged_scenarios(app, tag)
            else:
                views.view_my_scenarios(app)

         elif args.startswith('f'):
            if args.endswith('t'):
                tag = input('\ntag:')
                views.view_my_tagged_folders(app, tag)
            else:
                views.view_my_folders(app)

    elif command == 'get':
        if args.startswith('s'):
            if args.endswith('t'):
                tag = input('\ntag: ')
                views.view_tagged_scenarios(app, tag)
            else:
                views.view_published_scenarios(app)

        elif args.startswith('u'):
            user = input('\nusername: ')
            if args.endswith('s'):
                views.view_user_scenarios(app, user)
            elif args.endswith('f'):
                views.view_user_folders(app, user)
            else:
                views.view_users(app)
        
        elif args.startswith('f'):
            if args.endswith('t'):
                tag = input('\ntag: ')
                views.view_tagged_folders(app, tag)
            elif args.endswith('s'):
                folder_name = input('Folder name: ')
                views.view_folder(app, folder_name)
            else:
                views.view_public_folders(app)
    
    elif command == 'make':
        if args.startswith('s'):
            views.create_scenario(app)

    elif command == 'edit':
        if args.startswith('s'):
            views.edit_scenario(app)

    elif command == 'delete':
        if args.startswith('s'):
            views.delete_scenario(app)

    elif command == 'help':
        if args == 'adv':
            print(advanced_info)
        elif args == 'gen':
            print(overview)
        else:
            print(basic_info)

if __name__ == '__main__':
    app = App()
    while True:
        try:
            command(app)
        except (EOFError, KeyboardInterrupt):
            print('\nbye bye')

            app.session.close()

            sys.exit(SIGINT.value)
