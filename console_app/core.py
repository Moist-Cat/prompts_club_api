from requests import Session
import os
import json

#(XXX) 'member to change dis to prod url afterwards, baka.
URL = 'http://127.0.0.1:8000/api/'
#URL = 'https://moistcat.pythonanywhere.com/api/'

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

        if user_data:
            self.token = user_data['token']
            self.user = user_data['username']
            self.session.headers['Authorization'] = f'Token {self.token}'
    
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
            print('----- ERROR -----\n' \
                      f'{message}')
            return True
        return False

    # stolen from my auto tests (as planned)
    def create_object(self, obj_url, data):
        res = self.session.post(f'{URL}{obj_url}/make/', data=data)
        if not self.check_for_errors(res):
            return res.json()

    def edit_object(self, obj_url, data):
        res = self.session.put(f'{URL}{obj_url}/edit/', data=data)
        if not self.check_for_errors(res):
            return res.json()

    def get_object(self, obj_url):
        res = self.session.get(f'{URL}{obj_url}')
        if not self.check_for_errors(res):
            return res.json()

    def delete_object(self, obj_url):
        res = self.session.delete(f'{URL}{obj_url}/delete/')
        if not self.check_for_errors(res):
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
            self.session.headers['Authorization'] = f'Token {self.token}'
            
            with open('token.json', 'w') as file:
                 json.dump({'username': self.user,
                            'token': self.token}, file)
    def logout_user(self):
        # nothing fancy
        del self.session.headers['Authorization']
        self.user = ''
        self.token = ''
        
        print('logged out')
