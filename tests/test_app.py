
import os
import unittest

os.environ['TESTING'] = 'true'

from app import app, mydb, TimelinePost

class AppTestCase(unittest.TestCase):
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
    
    def test_home(self):
        response = self.client.get("/")
        assert response.status_code == 200
        html = response.get_data(as_text=True)
        assert "About Me" in html
        assert "Caktus Group" in html
        assert "MLH x Meta" in html
        # Tests navbar
        assert "/timeline" in html
    
    def test_timeline_works(self):
        response = self.client.get("/api/timeline_post")
        assert response.status_code == 200
        assert response.is_json

        json = response.get_json()
        assert "timeline_posts" in json
        assert len(json["timeline_posts"]) == 0

        post_response = self.client.post(
            "/api/timeline_post",
            data={
                "name": "Test User",
                "email": "test@example.com",
                "content": "My first timeline post",
            },
        )
        assert post_response.status_code == 200
        assert post_response.is_json

        created_post = post_response.get_json()
        assert created_post["name"] == "Test User"
        assert created_post["email"] == "test@example.com"
        assert created_post["content"] == "My first timeline post"
        assert "id" in created_post

        get_response = self.client.get("/api/timeline_post")
        assert get_response.status_code == 200
        assert get_response.is_json

        timeline_posts = get_response.get_json()["timeline_posts"]
        assert len(timeline_posts) == 1
        assert timeline_posts[0]["name"] == "Test User"
        assert timeline_posts[0]["email"] == "test@example.com"
        assert timeline_posts[0]["content"] == "My first timeline post"

        timeline_page_response = self.client.get("/timeline")
        assert timeline_page_response.status_code == 200
        timeline_page_html = timeline_page_response.get_data(as_text=True)
        assert "<title>Timeline</title>" in timeline_page_html

    def test_malformed_timeline_post(self):
        # POST request missing name
        response = self.client.post("/api/timeline_post", data={"email": "john@example.com",
        "content": "Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid name" in html
        
        # POST request with empty content
        response = self.client.post("/api/timeline_post", data=
        {"name": "John Doe", "email": "john@example.com", "content": ""})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid content" in html
        
        # POST request with malformed email
        response = self.client.post("/api/timeline_post", data=
        {"name": "John Doe", "email": "not-an-email", "content": "Hello world, I'm John!"})
        assert response.status_code == 400
        html = response.get_data(as_text=True)
        assert "Invalid email" in html
