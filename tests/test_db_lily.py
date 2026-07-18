# tests/test_db_lily.py
import datetime
import unittest

from peewee import SqliteDatabase

from app import TimelinePost

MODELS = [TimelinePost]

# use an in-memory SQLite for tests.
test_db = SqliteDatabase(':memory:')


class TestTimelinePostLily(unittest.TestCase):
    """Model-level tests complementing tests/test_db.py.

    test_db.py already covers basic create + retrieve of two posts, so
    this file focuses on field defaults, ordering, updates and deletes.
    """

    def setUp(self):
        test_db.bind(MODELS, bind_refs=False, bind_backrefs=False)
        test_db.connect()
        test_db.create_tables(MODELS)

    def tearDown(self):
        test_db.drop_tables(MODELS)
        test_db.close()

    def test_table_starts_empty(self):
        self.assertEqual(TimelinePost.select().count(), 0)

    def test_created_at_defaults_to_now(self):
        before = datetime.datetime.now()
        post = TimelinePost.create(
            name='Lily', email='lily@example.com', content='Hi')
        after = datetime.datetime.now()

        self.assertIsInstance(post.created_at, datetime.datetime)
        self.assertGreaterEqual(post.created_at, before)
        self.assertLessEqual(post.created_at, after)

    def test_explicit_created_at_is_respected(self):
        stamp = datetime.datetime(2020, 1, 1, 12, 0, 0)
        post = TimelinePost.create(
            name='Lily', email='lily@example.com',
            content='Hi', created_at=stamp)
        self.assertEqual(TimelinePost.get_by_id(post.id).created_at, stamp)

    def test_posts_order_by_created_at_desc(self):
        old = TimelinePost.create(
            name='Old', email='old@example.com', content='older post',
            created_at=datetime.datetime(2020, 1, 1))
        new = TimelinePost.create(
            name='New', email='new@example.com', content='newer post',
            created_at=datetime.datetime(2024, 1, 1))

        ordered = list(
            TimelinePost.select().order_by(TimelinePost.created_at.desc()))
        self.assertEqual([p.id for p in ordered], [new.id, old.id])

    def test_long_content_is_stored_intact(self):
        long_content = 'x' * 5000
        post = TimelinePost.create(
            name='Lily', email='lily@example.com', content=long_content)
        self.assertEqual(TimelinePost.get_by_id(post.id).content, long_content)

    def test_unicode_is_stored_intact(self):
        content = 'Sveiki no Rīgas! 日本語もOK'
        post = TimelinePost.create(
            name='Līga', email='liga@example.com', content=content)
        fetched = TimelinePost.get_by_id(post.id)
        self.assertEqual(fetched.content, content)
        self.assertEqual(fetched.name, 'Līga')

    def test_update_content(self):
        post = TimelinePost.create(
            name='Lily', email='lily@example.com', content='original')
        post.content = 'edited'
        post.save()
        self.assertEqual(TimelinePost.get_by_id(post.id).content, 'edited')

    def test_delete_removes_only_target_row(self):
        keep = TimelinePost.create(
            name='Keep', email='keep@example.com', content='stays')
        drop = TimelinePost.create(
            name='Drop', email='drop@example.com', content='goes')

        TimelinePost.delete().where(TimelinePost.id == drop.id).execute()

        remaining = list(TimelinePost.select())
        self.assertEqual(len(remaining), 1)
        self.assertEqual(remaining[0].id, keep.id)

    def test_delete_nonexistent_row_affects_nothing(self):
        TimelinePost.create(name='Lily', email='lily@example.com', content='Hi')
        deleted = TimelinePost.delete().where(TimelinePost.id == 9999).execute()
        self.assertEqual(deleted, 0)
        self.assertEqual(TimelinePost.select().count(), 1)


if __name__ == '__main__':
    unittest.main()