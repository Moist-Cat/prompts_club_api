import unittest
from requests import Session
import time

from django.utils.text import slugify

URL = "http://127.0.0.1:8000/api/"
# URL = 'https://moistcat.pythonanywhere.com/api/'

class TestAPI(unittest.TestCase):
    # --- initialization helpers ---
    def create_user(self, credentials):
        # create dummy user
        res = self.session.post(f"{URL}account/register/", data=credentials)
        self.user_id = res.json()["id"]
        try:
            assert res.status_code == 201
        except AssertionError as e:
            print(res.content)
            raise e
        return self.session.post(f"{URL}account/login/", data=credentials).json()[
            "token"
        ]

    # --- requests ---
    def create_object(self, obj_url, data):
        return self.session.post(f"{URL}{obj_url}/make/", data=data)

    def edit_object(self, obj_url, data):
        return self.session.put(f"{URL}{obj_url}/edit/", data=data)

    def get_object(self, obj_url):
        return self.session.get(f"{URL}{obj_url}")

    def delete_object(self, obj_url):
        return self.session.delete(f"{URL}{obj_url}/delete/")

    # --- other helpers ---
    def get_object_id(self, app, data, name):
        target_object = self.create_object(f"{app}/{name}", data)
        pk = target_object.json()["id"]
        return pk

    def get_object_slug(self, app, data, name):
        target_object = self.create_object(f"{app}/{name}", data)
        name = target_object.json()["name"]
        slug = slugify(name)
        return slug

    # --- initializer ---
    def setUp(self):
        self.session = Session()
        self.user = {"username": "dummy", "password": "toocommon123"}
        self.user_token = self.create_user(self.user)

        self.session.headers["Authorization"] = f"Token {self.user_token}"
        self.test_scenario = {
            "user": self.user_id,
            "title": "Dumy Scenario",
            "description": "A test scenario",
            "memory": "You are testing an scenario",
            "authors_note": "Focus on your relief after all the tests pass",
            "prompt": "Me.\r\nWorthless and good for nothing.\r\nTesting.",
            "nsfw": False,
            "status": "draft",
        }
        self.title_slug = slugify(self.test_scenario["title"])
        self.scenario_id = self.create_object("scenario", self.test_scenario).json()[
            "id"
        ]

        self.ratings = [
            {
                "value": 5,
                "scenario": self.scenario_id,
                "review": "Not bad, not bad.",
                "user": self.user_id,
            },
            {
                "value": 3,
                "scenario": self.scenario_id,
                "review": "Now u",
                "user": self.user_id,
            },
        ]

        self.world_info = [
            {
                "keys": "you, nobody, everyone",
                "entry": "you are a worthless code monke.",
                "scenario": self.scenario_id,
            },
            {
                "keys": "testing, test",
                "entry": "if you refuse to do tests your HP slowly decreases.",
                "scenario": self.scenario_id,
            },
        ]
        self.tag = [{"name": "WP"}, {"name": "PW"}]

        self.folder = [
            {
                "user": self.user_id,
                "name": "wholesome un-birth",
                "description": "W-what are you looking at, b-baka.",
                "status": "private",
                "parents": [],
            },
            {
                "user": self.user_id,
                "name": "test folder",
                "description": "I ran out of ideas.",
                "status": "private",
                "parents": [],
            },
        ]

    # --- destroya ---
    def tearDown(self):
        res = self.delete_object(f'account/{self.user["username"]}')
        try:
            self.assertEqual(res.status_code, 204)
        except AssertionError as e:
            print(res.content)
            raise e

        self.session.close()

    # --- assertion helpers ---
    def assertCreate(self, app, obj, data):
        try:
            res = self.create_object(f"{app}/{obj}", data)

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
                self.assertCreate(app, obj, value)

    def assertEdit(self, app, obj, data, field):
        try:
            data[field] = "3"

            res = self.edit_object(f"{app}/{obj}", data)

            self.assertEqual(res.status_code, 200)

            self.assertEqual("3", str(res.json()[field]))
        except AssertionError as e:
            print(res.content)
            raise e

    def assertDelete(self, app, obj):
        try:
            res = self.delete_object(f"{app}/{obj}")
            self.assertEqual(res.status_code, 204)
        except AssertionError as e:
            print(res.content)
            raise e

    def assertGet(self, app, obj, data):
        try:
            res = self.get_object(f"{app}/{obj}")
            self.assertEqual(res.status_code, 200)
            results = res.json()["results"]
            try:
                for key, value in data.items():
                    self.assertIn(key, results.keys())
                    self.assertIn(value, results.values())
            except AttributeError as e:
                for key, value in data.items():
                    self.assertIn(key, results[0].keys())
                    self.assertIn(value, results[0].values())
        except AssertionError as e:
            print(res.content)
            raise e

    # --- tests ---
    # Scenario tests
    def testEditScenario(self):
        self.assertEdit("scenario", f"{self.title_slug}", self.test_scenario, "title")

    def testShowsPrivateContent(self):
        # since we do not serialize the whole data in the
        # list, we have to conform with knowing the title is there.
        # (since)
        self.assertGet("scenario", "mine", {"title": self.test_scenario["title"]})

    def testPrivateScenarioIsHidden(self):
        try:
            self.assertGet("scenario", "", self.test_scenario)
        except (IndexError, AssertionError):
            # meaning there is nothing there
            # or at least not the scenario
            pass
        else:
            raise Exception("Private scenario shows up in public list")

    # WI tests
    def testCreateWI(self):
        self.assertCreate("scenario", "worldinfo", self.world_info)

    def testEditWI(self):
        world_info = self.world_info[0]
        id = self.get_object_id("scenario", world_info, "worldinfo")

        self.assertEdit("scenario", f"worldinfo/{id}", world_info, "entry")

    def testDeleteWI(self):
        world_info = self.world_info[0]
        id = self.get_object_id("scenario", world_info, "worldinfo")

        self.assertDelete("scenario", f"worldinfo/{id}")

    # Rating tests
    def testCreateRatings(self):
        # notice how it should fail the second time
        # since we allow only one rating per user
        self.assertCreate("scenario", f"rating", self.ratings[0])
        try:
            self.assertCreate("scenario", f"rating", self.ratings[1])
        except AssertionError:
            pass
        else:
            raise Exception("User is able to create two reviews in the " \
                            "same scenario")

    def testEditRatings(self):
        rating = self.ratings[0]
        id = self.get_object_id("scenario", rating, "rating")

        self.assertEdit("scenario", f"rating/{id}", rating, "value")

    def testDeleteRating(self):
        rating = self.ratings[0]
        id = self.get_object_id("scenario", rating, "rating")

        self.assertDelete("scenario", f"rating/{id}")

    # Tag tests
    def testCreateTag(self):
        self.assertCreate("scenario", f"{self.title_slug}/tag", self.tag)

    def testDeleteTag(self):
        tag_data = self.tag[0]
        tag = self.create_object(f"scenario/{self.title_slug}/tag", tag_data)
        # luckily, we get the slug outright, so no
        # need to slugify afterwards
        tag_id = tag.json()["id"]
        self.assertDelete("scenario", f"{self.title_slug}/tag/{tag_id}")

    def testScenarioHiddenFilterByTags(self):
        tag_data = self.tag[0]
        tag = self.create_object(f"scenario/{self.title_slug}/tag", tag_data)
        tag_slug = tag.json()["slug"]
        try:
            self.assertGet("scenario", f"tag/{tag_slug}", tag_data)
        except (IndexError, AssertionError):
            pass
        else:
            raise Exception("Private scenario tags show up in public list")

    def testTagList(self):
        tag_data = self.tag[0]
        self.create_object(f"scenario/{self.title_slug}/tag", tag_data)

        self.assertGet("scenario", f"{self.title_slug}/tag", tag_data)

    def testScenarioTags(self):
        tag_data = self.tag[0]
        tag = self.create_object(f"scenario/{self.title_slug}/tag", tag_data)
        self.assertGet("scenario", f"{self.title_slug}/tag", tag_data)

    # folder tests
    def testCreateFolder(self):
        self.assertCreate("account", "folder", self.folder)

    def testEditFolder(self):
        folder = self.folder[0]
        slug = self.get_object_slug("account", folder, "folder")

        self.assertEdit("account", f"folder/{slug}", folder, "name")

    def testDeleteFolder(self):
        folder = self.folder[0]
        slug = self.get_object_slug("account", folder, "folder")

        self.assertDelete("account", f"folder/{slug}")

    def testAddToFolder(self):
        folder = self.folder[0]
        slug = self.get_object_slug("account", folder, "folder")

        self.session.post(
            f"{URL}account/folder/{slug}/add/{self.scenario_id}/",
            data={"contentype": "scenario"},
        )
        self.assertGet(
            "account",
            f"folder/{slug}/scenarios",
            {"title": self.test_scenario["title"]},
        )

    def testShowPrivateFolder(self):
        folder = self.folder[0]
        self.create_object("account/folder", folder)

        self.assertGet("account", "folder/mine", folder)


if __name__ == "__main__":
    unittest.main()
