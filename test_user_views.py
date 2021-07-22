"""Message View tests."""
import os
from unittest import TestCase

from models import db, connect_db, Message, User
os.environ['DATABASE_URL'] = "postgresql:///warbler_test"
from app import app, CURR_USER_KEY
db.create_all()
app.config['WTF_CSRF_ENABLED'] = False    
    
class UserViewTestCase(TestCase):
    """Test views for Users."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.test_user0 = User.signup(username="testuser0",
                                    email="test0@test.com",
                                    password="testuser0",
                                    image_url=None)
        self.test_user1 = User.signup(username="testuser1",
                                    email="test1@test.com",
                                    password="testuser1",
                                    image_url=None)
        self.test_user2 = User.signup(username="testuser2",
                                    email="test2@test.com",
                                    password="testuser2",
                                    image_url=None) 
        self.test_user3 = User.signup(username="testuser3",
                                    email="test3@test.com",
                                    password="testuser3",
                                    image_url=None)                                     

        self.user0_id = 100000                                
        self.user1_id = 100001                                   
        self.user2_id = 100002
        self.user3_id = 100003

        self.test_user0.id = self.user0_id                                  
        self.test_user1.id = self.user1_id                                  
        self.test_user2.id = self.user2_id  
        self.test_user3.id = self.user3_id  

        db.session.commit()

    def tearDown(self):
        """Roll back db.session"""
        db.session.rollback()
        

    def test_logged_in_view_user_followers(self):
        """If a user is logged in and tries to view a user's followers,
           check to see if followers display"""

        self.test_user0.followers.append(self.test_user1)
        self.test_user0.followers.append(self.test_user2)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.get(f"/users/{sess[CURR_USER_KEY]}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("@testuser1", str(resp.data))
            self.assertIn("@testuser2", str(resp.data))
            self.assertNotIn("@testuser3", str(resp.data))
    
    def test_not_logged_in_view_user_followers(self):
        """If a user isn't logged in and tries to view a user's followers,
           response 200 should be returned"""

        with self.client as c:
            resp = c.get(f"/users/{self.test_user0.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))