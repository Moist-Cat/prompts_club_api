import unittest
from requests import Session

from django.utils.text import slugify

URL = 'http://127.0.0.1:8000/api/'

class TestScenarios(unittest.TestCase):
    # --- initialization helpers ---
    def create_user(self, credentials):
        # create dummy user
        res = self.session.post(f'{URL}account/register/',
                                data=credentials)
        try:
            assert res.status_code == 201
        except AssertionError as e:
            print(res.content)
            raise e
        return self.session.post(f'{URL}account/login/',
                                data=credentials).json()['token']
    # --- requests ---
    def create_object(self, obj_url, data):
        return self.session.post(f'{URL}{obj_url}/create/', data=data)

    def edit_object(self, obj_url, data):
        return self.session.put(f'{URL}{obj_url}/edit/', data=data)

    def get_object(self, obj_url):
        return self.session.get(f'{URL}{obj_url}/')

    def delete_object(self, obj_url):
        return self.session.delete(f'{URL}{obj_url}/delete/')

    # --- other helpers ---
    def get_id_for_related_field(self, data, name):
        self.create_object(f'scenario/{name}', data)
        target_scenario = self.get_object('scenario/'
                                         f'{self.title_slug}')
        print(target_scenario.json())
        try:
            pk = target_scenario.json()[f'{name}'][0]['id']
        except KeyError:
            pk = target_scenario.json()[f'{name}_set'][0]['id']
        return pk


    # --- initializer ---
    def setUp(self):
        self.user = {'username':'dummy', 'password':'toocommon123'}
        self.session = Session()
        self.user_token = self.create_user(self.user)
        self.user_id = self.get_object(f'account/{self.user["username"]}').json()['id']
        
        self.session.headers['Authorization'] = f'Token {self.user_token}'
        self.session.headers['Content-Type']: "application/json"
        self.test_scenario = {
                             'author': self.user_id,
                             'title': 'Dumy Scenario',
                             'description': 'A test scenario',
                             'memory': 'You are testing an scenario',
                             'authors_note': 'Focus on your relief after all the tests pass',
                             'prompt': 'Me.\r\nWorthless and good for nothing.\r\nTesting.',
                             'nsfw': False,
                             'status': 'draft'
        }
        self.title_slug = slugify(self.test_scenario['title'])
        self.scenario_id = self.create_object('scenario',
                               self.test_scenario).json()['id']

        self.ratings = [
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
        
        self.world_info = [{
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
        self.tag = {
                    'name': 'WP'
        }

    # --- destroya ---
    def tearDown(self):
      res = self.delete_object(f'account/{self.user["username"]}')
      try:
          self.assertEqual(res.status_code, 204)
      except AssertionError as e:
          print(res.content)
          raise e

    # --- assertion helpers ---
    def assertCreate(self, obj_url, data):
        try:
            res = self.create_object(obj_url, data)
            self.assertEqual(res.status_code, 201)

            for key, value in data.items():
               self.assertIn(key, res.json().keys())
               self.assertIn(value, res.json().values())
        except AssertionError as e:
            print(res.content)
            raise e
        except ValueError as e:
            # a.k.a: it is a list, meaning is not an scenario
            for value in data:
                self.assertCreate(obj_url, value)
        else:
            # we make sure that the WIs and such are pointing
            # to the correct scenario
            self.scenario_id = res.json()['id']

    def assertEdit(self, obj_url, data, field):
        try:
            data[field] = '3'

            res = self.edit_object(f'scenario/{obj_url}', data=data)

            self.assertEqual(res.status_code, 200)

            self.assertEqual('3', str(res.json()[field]))
        except AssertionError as e:
            print(res.content)
            raise e

    def assertDelete(self, obj_url):
        try:
            res = self.delete_object(f'scenario/{obj_url}')
            self.assertEqual(res.status_code, 204)
        except AssertionError as e:
            print(res.content)
            raise e

    def assertGet(self, obj_url, data):
        try:
            res = self.get_object(obj_url)
            self.assertEqual(res.status_code, 200)
            try:
                for key, value in data.items():
                    self.assertIn(key, res.json().keys())
                    self.assertIn(value, res.json().values())
            except AttributeError as e:
                for key, value in data.items():
                    self.assertIn(key, res.json()[0].keys())
                    self.assertIn(value, res.json()[0].values())
        except AssertionError as e:
            print(res.content)
            raise e

    # --- tests --- 
    # Scenario tests
    def testEditScenario(self):
        self.assertEdit(f'{self.title_slug}',self.test_scenario, 'title')

    def testShowsPrivateContent(self):
        self.assertGet('scenario/mine', self.test_scenario)

    def testPrivateScenarioIsHidden(self):
        try:
            self.assertGet('scenario', self.test_scenario)
        except (IndexError, AssertionError):
            # meaning there is nothing there
            # or at least not the scenario
            pass
        else:
            raise Exception('Private scenario shows up in public list')


    # WI tests
    def testCreateWI(self):
        self.assertCreate('scenario/worldinfo', self.world_info)

    def testEditWI(self):
        world_info = self.world_info[0]
        id = self.get_id_for_related_field(world_info, 'worldinfo')

        self.assertEdit(f'worldinfo/{id}', world_info, 'entry')
        
    def testDeleteWI(self):
        world_info = self.world_info[0]
        id = self.get_id_for_related_field(world_info, 'worldinfo')

        self.assertDelete(f'worldinfo/{id}')
        
    # Rating tests
    def testCreateRatings(self):
        # notice how it should fail the second time
        # since we allow only one rating per user
        self.assertCreate('scenario/rating', self.ratings[0])
        try:
            self.assertCreate('scenario/rating',
                                            self.ratings[1]),
        except AssertionError:
            pass
        else:
           raise Exception('User is able to create two reviews in the'
                           'same scenario')
        
    def testEditRatings(self):
        rating = self.ratings[0]
        id = self.get_id_for_related_field(rating, 'rating')

        self.assertEdit(f'rating/{id}', rating, 'value')
        

    def testDeleteRating(self):
        rating = self.ratings[0]
        id = self.get_id_for_related_field(rating, 'rating')

        self.assertDelete(f'rating/{id}')
    
    def testCreateTag(self):
        self.assertCreate(f'scenario/{self.title_slug}/tag', self.tag)
        

    # Folder tests
    def testCreateFolder(self):
        pass
    # Comment tests
if __name__ == '__main__':
    unittest.main()
