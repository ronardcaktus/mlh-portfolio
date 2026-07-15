import unittest
from peewee import *

from app import TimelinePost

MODELS = [TimelinePost]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')

class TestTimelinePost(unittest.TestCase):

    user_1 = dict(name='John Doe', email='john@example.com', content='Hello world, I\'m John!')
    user_2 = dict(name='Jane Doe', email='jame@example.com', content='Hello world, I\'m Jane!')

    def setUp(self):
        # Bind model classes to test db. 
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)
    
    def tearDown(self):
        test_db.drop_tables (MODELS)
        test_db.close()

    def test_timeline_post(self) :
        first_post = TimelinePost.create(**self.user_1)
        assert first_post.id == 1
        second_post = TimelinePost.create(**self.user_2)
        assert second_post. id == 2

        post_1 = TimelinePost.get_by_id(1)
        self.assertEqual(post_1.name, self.user_1['name'])
        self.assertEqual(post_1.email, self.user_1['email'])
        self.assertEqual(post_1.content, self.user_1['content'])

        post_2 = TimelinePost.get_by_id(2)
        self.assertEqual(post_2.name, self.user_2['name'])
        self.assertEqual(post_2.email, self.user_2['email'])
        self.assertEqual(post_2.content, self.user_2['content'])
        