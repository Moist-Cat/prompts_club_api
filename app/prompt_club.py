from requests import Session

import tkinter
from tkinter import Frame, Button, Label, StringVar, \
                    Entry
from tkinter.messagebox import showerror, showinfo

import json

#(XXX) 'member to change dis to prod url afterwards, baka.
URL = 'http://127.0.0.1:8000/api/'

## configs
font = "Times News Roman"
# buttons
butt_base = {'bg':'magenta', 'activebackground':'pink','borderwidth':3, 'wraplength': False,
            'pady': 10, 'padx':10, 'font':[font, 10], 'justify':'center'}
# labels
lab_base = {'bg':'black', 'fg':'gray', 'borderwidth':1, 'highlightthickness':False,
        'wraplength': False, 'pady': 10, 'padx':10,'font':[font, 10], 'justify':'center'}

entry_base = {'bg':'grey', 'fg':'white', 'borderwidth':1, 'highlightthickness':True,
              'font':[font, 10], 'justify':'center'}

frame_base = {'bg': 'black', 'name':'main'}

frame_header = {'bg': 'grey', 'name':'header'}

frame_scenario = {'bg': 'grey', 'highlightthickness':True, 'name': 'scenario'}


# decorators
def clean_and_set_up(param_function):
    """
    To switch between frames, very convenient.
    But I think it still needs some work.
    """
    def inner_function(*args, **kwargs):
        cls = args[0]
        root = cls.root
        frame = args[-1]
        frame_name = frame.__str__().strip('.')
        
        try: #to destroy the frame
            frame.destroy()
        except AttributeError:
            pass
        if frame_name == 'header':
           cls.MainFrame = Frame(root, **frame_header)
           cls.MainFrame.pack()
           frame = cls.MainFrame
        else:
            frame = Frame(root, **frame_base)
            frame.pack()

        param_function(cls, frame)
    return inner_function

class App(object):
    def load_user_data(self):
        try:
            with open('token.json') as file:
                return json.load(file)
        except:
            return

    def __init__(self):
        self.session = Session()

        user_data = self.load_user_data()

        self.root = tkinter.Tk()
        self.root.title('Prompts Club')
        self.root.geometry('1200x720')
        self.root.config(bg='black')

        self.MainFrame = Frame(self.root, **frame_header)
        self.MainFrame.pack()
        if user_data:
            self.token = user_data['token']
            self.user = user_data['username']

            self.auth_user_main_frame(self.MainFrame)
        else:
            self.anon_user_main_frame(self.MainFrame)

    # --- Main frames ---
    # One of those must be always active on top.
    # Serves as a quick menu.
    @clean_and_set_up
    def auth_user_main_frame(self, frame=None):
        self.session.headers['Authorization'] = f'Token {self.token}'
        main_label = Label(frame,
                   text=f'Welcome, {self.user}.',
                   **lab_base)
        main_label.config(bg='dark gray')
        main_label.grid(row=0, column=0)
        
        logout_button = Button(frame, command=lambda: self.logout_user(),
                    text='Log-out', **butt_base)
        logout_button.grid(row=0, column=1)
        self.dashboard_window()

    @clean_and_set_up
    def anon_user_main_frame(self, frame=None):
        main_label = Label(frame,
                   text='Welcome, Anon. You can read anything you want, ' \
                        'but you need an account to create content for ' \
                        'the platform.\nIt makes my life easier, ' \
                        'please understand.',
                   **lab_base)
        main_label.config(bg='dark gray')
        main_label.grid(row=0, column=0)
        log_in_button = Button(frame, command=lambda: self.enter_window(),
                    text='Log-in' ,**butt_base)
        log_in_button.grid(row=0, column=1)
        self.init_window()
    
    # --- helper methods ---
    def check_for_errors(self, res):
        if res.status_code > 399:
            # there is an error
            message = ''
            for key, value in res.json().items():
                # since the response often comes as a list
                value = ''.join(value)
                key = key.capitalize()
                message += f'{key}: {value}\n'
            showerror(title='Uh-oh, something went wrong',
                                 message=message)
            return True
        return False

    # stolen from my auto tests (as planned)
    def create_object(self, obj_url, data):
        res = self.session.post(f'{URL}{obj_url}/make/', data=data)
        self.check_for_errors(res)

        return res.json()

    def edit_object(self, obj_url, data):
        res = self.session.put(f'{URL}{obj_url}/edit/', data=data)
        self.check_for_errors(res)

        return res.json()
 
    def get_object(self, obj_url):
        res = self.session.get(f'{URL}{obj_url}')
        self.check_for_errors(res)
 
        return res.json()
 
    def delete_object(self, obj_url):
        res = self.session.delete(f'{URL}{obj_url}/delete/')
        self.check_for_errors(res)

        return res.json()

    def create_user(self, credentials):
        # create dummy user
        res = self.session.post(f'{URL}account/register/',
                                data=credentials)
        if not self.check_for_errors(res):
            self.login_user(credentials)

    def login_user(self, credentials):
        res =  self.session.post(f'{URL}account/login/',
                                data=credentials)
        if not self.check_for_errors(res):
            self.user = credentials['username']
            self.token = res.json()['token']
            with open('token.json', 'w') as file:
                 json.dump({'username': self.user,
                            'token': self.token}, file)
            
            showinfo('Success', f'Welcome (back?), {self.user}. '
                                 'Your daily dose of \'stuff\' awaits you.')

            self.auth_user_main_frame(self.MainFrame)

    def logout_user(self):
        # nothing fancy
        del self.session.headers['Authorization']
        
        self.anon_user_main_frame(self.MainFrame)

    # --- tkinter-based views ---
    def show_scenarios(self, frame, query):
       query = query.get()
       if query.starts_with('#'):
           # meaning we need to look for a tag
           res = self.get_object(f'scenario/tag/{query}')
           data = res.json()
       elif query.starts_with('$'):
           res = self.get_object(f'account/{query}/content/')
       elif query:
           # A title
           res = 
      
        
    
    @clean_and_set_up
    def init_window(self, frame=None):
        welcome = 'Create an account to start making scenarios ' \
                  'or browse what other people have made.'
        welcome_label = Label(frame, text=welcome, **lab_base)
        welcome_label.grid(row=0,column=0, columnspan=2, pady=100)

        goto_enter = Button(frame, command=lambda: self.enter_window(frame),
                        text='Join', **butt_base)
        goto_enter.grid(row=1,column=0)
        goto_browse = Button(frame, command=lambda:self.browse_window(frame),
                        text='Browse', **butt_base)
        goto_browse.grid(row=1,column=1)

    @clean_and_set_up
    def enter_window(self, frame=None):
        username = StringVar()
        password = StringVar()
        
        register_label = Label(frame, text='Log in or register.', **lab_base)
        register_label.grid(row=0,column=0, columnspan=2, pady=100)
        
        username_label = Label(frame, text='Username', **lab_base)
        username_label.grid(row=1,column=0)
        username_entry = Entry(frame, textvariable = username, **entry_base)
        username_entry.grid(row=1,column=1)

        password_label = Label(frame, text='Password', **lab_base)
        password_label.grid(row=2,column=0)
        password_entry = Entry(frame, textvariable = password, **entry_base)
        password_entry.grid(row=2,column=1)

        register_button = Button(frame, command=lambda:self.create_user(
                                        {'username': username.get(),
                                         'password': password.get()}),
                        text='Create', **butt_base)
        register_button.grid(row=3,column=0)
        register_button = Button(frame, command=lambda:self.login_user(
                                        {'username': username.get(),
                                         'password': password.get()}),
                        text='Log-in', **butt_base)
        register_button.grid(row=3,column=1)

    @clean_and_set_up
    def dashboard_window(self, frame=None):
        query = StringVar()
        

        search_bar_label = Label(frame, text='Search title, insert \"#\" ' \
                                             'to search a particular tag or' \
                                             '\'$\' to look for a particular' \
                                             'user\'s content.', **lab_base)
        search_bar_label.grid(row=0,column=0)  
        search_bar_entry = Entry(frame, textvariable = query, **entry_base)
        search_bar_entry.grid(row=1,column=0)
        
        self.show_scenarios(frame, query)
        
if __name__ == '__main__':
    app = App()
    app.root.mainloop()
