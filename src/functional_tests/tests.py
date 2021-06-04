import unittest
from requests import Session

from django.utils.text import slugify

class AnonTestScenarios(unittest.TestCase):
    def _create_user(self, credentials):
        # create dummy user
        res = self.session.post('http://127.0.0.1:8000/api/account/register/',
                                data=credentials)
        try:
            assert res.status_code == 201
        except AssertionError as e:
            print(res.content)
            raise e
        return self.session.post('http://127.0.0.1:8000/api/account/login/',
                                data=credentials).json()['token']

    def _get_user_id(self, username):
        res = self.session.get(f'http://127.0.0.1:8000/api/account/{username}/')
        return res.json()['id']

    def setUp(self):
        self.user = {'username':'dummy', 'password':'toocommon123'}
        self.session = Session()
        self.user_token = self._create_user(self.user)
        self.user_id = self._get_user_id(self.user['username'])
        
        self.session.headers['Authorization'] = f'Token {self.user_token}'
        self.url = 'http://127.0.0.1:8000/api/'
        self.test_scenario = {
                             'author': self.user_id,
                             'title': 'Dumy Scenario',
                             'description': 'A test scenario',
                             'memory': 'You are testing an scenario',
                             'authors_note': 'Focus on your relief after all the tests pass',
                             'prompt': 'Me.\r\nWorthless and good for nothing.\r\nTesting.',
                             'nsfw': False,
                             'status': 'published'
        }
        self.scenario_id = 0

    def tearDown(self):
      res = self.session.delete(self.url + f'account/delete/{self.user["username"]}/')
      try:
          assert res.status_code == 204
      except AssertionError as e:
          print(res.content)
          
    def _create_object(self, obj_url, data):
        return self.session.post(self.url + obj_url, data=data)

    def assertCreate(self, obj_url, data):
        try:
            response = self.session.post(self.url + obj_url, data=data)

            self.assertEqual(response.status_code, 201)

            for key, value in data.items():
               self.assertIn(key, response.json().keys())
               self.assertIn(value, response.json().values())

        except AssertionError as e:
            print(response.content)
            raise e
        except ValueError as e:
            # a.k.a: it is a list, meaning is not an scenario
            for value in data:
                self.assertCreate(obj_url=obj_url, data=value)
        else:
            # we make sure that the WIs and such are pointing
            # to the correct scenario
            self.scenario_id = response.json()['id']
    
    def testCreate(self):
        self.assertCreate('scenario/create/', self.test_scenario)

    def testCreateWI(self):
        self.assertCreate('scenario/create/', self.test_scenario)

        world_info = [{
                           'keys': 'you, nobody, everyone',
                           'entry': 'you are a worthless code monke.',
                           'scenario': self.scenario_id
                           },
                           {
                           'keys': 'testing, test',
                           'entry': 'if you refuse to do tests your HP slowly decreases.', 
                           'scenario': self.scenario_id
                           }
        ]

        self.assertCreate('scenario/create/wi/', world_info)

    def testEditScenario(self):
        self.assertCreate('scenario/create/', self.test_scenario)

        # since we seach the scenarios based in the slug...
        old_title = slugify(self.test_scenario["title"])
        self.test_scenario["title"] = 'another_title'

        response = self.session.put(self.url + f'scenario/edit/{old_title}/',
                                     data=self.test_scenario)
        self.assertEqual('another_title', response.json()['title'])
    
    def testCreateRatings(self):
        self.assertCreate('scenario/create/', self.test_scenario)

        ratings = [
                           {
                           'value': 5,
                           'scenario': self.scenario_id,
                           'user': self.user_id,
                           },
                           {
                           'value': 3,
                           'scenario': self.scenario_id,
                           'user': self.user_id,
                           }
        ]
        # notice how it should fail the second time
        # since we allow only one rating per user
        self.assertCreate('scenario/create/rating/', ratings[0])
        try:
            self.assertCreate('scenario/create/rating/',
                                            ratings[1]),
        except AssertionError:
            pass
        else:
           raise Exception('User is able to create two reviews in the'
                           'same scenario')
    def testCreateFolder(self):
        self.assertCreate()
if __name__ == '__main__':
    unittest.main()
