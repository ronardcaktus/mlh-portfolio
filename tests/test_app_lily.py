# tests/test_app_lily.py
import os
import unittest

os.environ['TESTING'] = 'true'

from app import app, mydb, TimelinePost


class AppTestCaseLily(unittest.TestCase):
    """Integration tests complementing tests/test_app.py.

    test_app.py covers the home page, the timeline GET/POST happy path and
    the three basic validation errors, so this file covers the remaining
    pages, the DELETE endpoint and further edge cases.
    """

    @classmethod
    def setUpClass(cls):
        mydb.connect(reuse_if_open=True)
        mydb.create_tables([TimelinePost])

    @classmethod
    def tearDownClass(cls):
        mydb.drop_tables([TimelinePost])
        if not mydb.is_closed():
            mydb.close()

    def setUp(self):
        TimelinePost.delete().execute()
        self.client = app.test_client()

    def _create_post(self, name='Test User', email='test@example.com',
                     content='Some content'):
        response = self.client.post(
            '/api/timeline_post',
            data={'name': name, 'email': email, 'content': content})
        self.assertEqual(response.status_code, 200)
        return response.get_json()

    # --- pages ---

    def test_hobbies_page(self):
        response = self.client.get('/hobbies')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    def test_travel_locations_page(self):
        response = self.client.get('/travel-locations')
        self.assertEqual(response.status_code, 200)
        self.assertIn('text/html', response.content_type)

    def test_unknown_page_returns_404(self):
        response = self.client.get('/no-such-page')
        self.assertEqual(response.status_code, 404)

    # --- GET /api/timeline_post ---

    def test_multiple_posts_returned_newest_first(self):
        self._create_post(name='First', content='oldest')
        self._create_post(name='Second', content='middle')
        self._create_post(name='Third', content='newest')

        posts = self.client.get(
            '/api/timeline_post').get_json()['timeline_posts']
        self.assertEqual(len(posts), 3)
        self.assertEqual({p['name'] for p in posts},
                         {'First', 'Second', 'Third'})

        timestamps = [p['created_at'] for p in posts]
        self.assertEqual(timestamps, sorted(timestamps, reverse=True))

    def test_created_post_has_expected_fields(self):
        created = self._create_post()
        for field in ('id', 'name', 'email', 'content', 'created_at'):
            self.assertIn(field, created)

    # --- POST edge cases ---

    def test_post_with_no_data_at_all(self):
        response = self.client.post('/api/timeline_post', data={})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid name', response.get_data(as_text=True))

    def test_post_missing_email(self):
        response = self.client.post(
            '/api/timeline_post',
            data={'name': 'John Doe', 'content': 'Hello'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email', response.get_data(as_text=True))

    def test_post_email_without_domain_dot(self):
        response = self.client.post(
            '/api/timeline_post',
            data={'name': 'John Doe', 'email': 'john@example',
                  'content': 'Hello'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email', response.get_data(as_text=True))

    def test_post_email_with_spaces_rejected(self):
        response = self.client.post(
            '/api/timeline_post',
            data={'name': 'John Doe', 'email': 'john doe@example.com',
                  'content': 'Hello'})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Invalid email', response.get_data(as_text=True))

    def test_invalid_post_is_not_saved(self):
        self.client.post(
            '/api/timeline_post',
            data={'name': 'John Doe', 'email': 'bad-email',
                  'content': 'Hello'})
        posts = self.client.get(
            '/api/timeline_post').get_json()['timeline_posts']
        self.assertEqual(len(posts), 0)

    # --- DELETE /api/timeline_post/<id> ---

    def test_delete_removes_post(self):
        created = self._create_post()
        response = self.client.delete(f"/api/timeline_post/{created['id']}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.get_json()['deleted'], created['id'])

        posts = self.client.get(
            '/api/timeline_post').get_json()['timeline_posts']
        self.assertEqual(len(posts), 0)

    def test_delete_missing_post_returns_404(self):
        response = self.client.delete('/api/timeline_post/99999')
        self.assertEqual(response.status_code, 404)
        self.assertIn('error', response.get_json())

    def test_delete_twice_returns_404_second_time(self):
        created = self._create_post()
        self.client.delete(f"/api/timeline_post/{created['id']}")
        response = self.client.delete(f"/api/timeline_post/{created['id']}")
        self.assertEqual(response.status_code, 404)

    def test_delete_only_removes_target_post(self):
        keep = self._create_post(name='Keep', content='stays')
        remove = self._create_post(name='Remove', content='goes')

        self.client.delete(f"/api/timeline_post/{remove['id']}")

        posts = self.client.get(
            '/api/timeline_post').get_json()['timeline_posts']
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['id'], keep['id'])


if __name__ == '__main__':
    unittest.main()