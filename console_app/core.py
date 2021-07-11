from requests import Session
import os
import json
import time

URL = 'http://127.0.0.1:8000/api/'
#URL = 'https://moistcat.pythonanywhere.com/api/'

# error messages that we do not need to show to 
# the user
safe_messages = ()
was_throttled = 'throttled'

class TooManyRequests(Exception):
    pass

def retry_when_throttle(param_funct):
    # this could be dangerous, since users could 
    # be mindlessly DDoS-ing the site (contrary to what 
    # we intended to do with throttling) so we must limit 
    # the retries and send a message to the user.
    def inner_function(*args, **kwargs):
        for i in range(5):
            try:
                return param_funct(*args, **kwargs)
            except TooManyRequests:
                time.sleep(1.1)
            else:
                # success
                break
        else:
            # more than 5 failures, backend is down or 
            # there is an error.
            print('Server is down, please be patient.')
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

        if user_data:
            self.token = user_data['token']
            self.user = user_data['username']
            self.session.headers['Authorization'] = f'Token {self.token}'

    def __delete__(self):
        self.session.close()
    
    # --- helper methods ---
    def check_for_errors(self, res):
        if res.status_code > 399:
            # there is an error
            message = ''
            try:
                for key, value in res.json().items():
                    # since the response often comes as a list
                    error = key.capitalize()
                    description = ''.join(value)
                    if was_throttled in description:
                        raise TooManyRequests
                    message += f'{error}: {description}\n'
                print('----- ERROR -----\n' \
                          f'{message}')
            except json.decoder.JSONDecodeError:
                print('Hmm... it seems like there was '
                      'something wrong with that url.')
            return True
        return False

    # stolen from my auto tests (as planned)
    @retry_when_throttle
    def create_object(self, obj_url, data):
        res = self.session.post(f'{URL}{obj_url}/make/', data=data)
        if not self.check_for_errors(res):
            return res.json()

    @retry_when_throttle
    def edit_object(self, obj_url, data):
        res = self.session.put(f'{URL}{obj_url}/edit/', data=data)
        if not self.check_for_errors(res):
            return res.json()

    @retry_when_throttle
    def get_object(self, obj_url):
        res = self.session.get(f'{URL}{obj_url}')
        if not self.check_for_errors(res):
            return res.json()

    @retry_when_throttle
    def delete_object(self, obj_url):
        res = self.session.delete(f'{URL}{obj_url}/delete/')
        self.check_for_errors(res)

    @retry_when_throttle
    def create_user(self, credentials):
        # create dummy user
        res = self.session.post(f'{URL}account/register/',
                                data=credentials)
        if not self.check_for_errors(res):
            self.login_user(credentials)

    @retry_when_throttle
    def login_user(self, credentials):
        res = self.session.post(f'{URL}account/login/',
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
