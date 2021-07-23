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

        user0 = User.signup(
                            username='test0', 
                            email='test0@email.com', 
                            password='password0',
                            image_url=None)
        user1 = User.signup(
                            username='test1', 
                            email='test1@email.com', 
                            password='password1', 
                            image_url=None)
        user2 = User.signup(
                            username='test2', 
                            email='test2@email.com', 
                            password='password2', 
                            image_url=None)
        user3 = User.signup(
                            username='test3', 
                            email='test3@email.com', 
                            password='password3',
                            image_url=None)                               

        db.session.commit()

        self.user0 = user0                             
        self.user1 = user1                                   
        self.user2 = user2
        self.user3 = user3

        self.user0_id = user0.id                                
        self.user1_id = user1.id                                   
        self.user3_id = user3.id
        self.user2_id = user2.id

    def tearDown(self):
        """Roll back db.session"""
        db.session.rollback()
        

    def test_logged_in_view_user_followers(self):
        """If a user is logged in and tries to view a user's followers,
           check to see if followers display"""

        self.user0.followers.append(self.user1)
        self.user0.followers.append(self.user2)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.get(f"/users/{sess[CURR_USER_KEY]}/followers")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test2", str(resp.data))

            self.assertNotIn("@test3", str(resp.data))
    
    def test_not_logged_in_view_user_followers(self):
        """If a user isn't logged in and tries to view a user's followers,
           redirect to response 200, flash access unauthorized"""

        with self.client as c:
            resp = c.get(f"/users/{self.user0.id}/followers", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_users_page(self):
        """Does the page display other users"""

        with self.client as c:
            resp = c.get("/users")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@test1", str(resp.data))
            self.assertIn("@test2", str(resp.data))
            self.assertIn("@test3", str(resp.data))

    def test_users_search(self):
        """Does the users page successfully search other users"""

        with self.client as c:
            resp = c.get("/users?q=test1")

            self.assertEqual(resp.status_code, 200)

            self.assertIn("@test1", str(resp.data))

            self.assertNotIn("@test2", str(resp.data))
            self.assertNotIn("@test3", str(resp.data))

    def test_user_follow(self):
        """Can a user follow another user"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.post(f"/users/follow/{self.user1_id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("@test1", str(resp.data))

    def test_not_logged_in_follow(self):
        """if a not logged in user tries to follow someone, 
           unauthorized redirect should occur"""

        with self.client as c:

            resp = c.post(f"/users/follow/{self.user1_id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_user_unfollow(self):
        """Can a user unfollow another user"""

        self.user0.following.append(self.user1)

        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.post(f"/users/stop-following/{self.user1_id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertNotIn("@test1", str(resp.data))

    def test_not_logged_in_unfollow(self):
        """if a not logged in user tries to unfollow someone, 
           unauthorized redirect should occur"""

        with self.client as c:

            resp = c.post(f"/users/stop-following/{self.user1_id}", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_edit_user_profile(self):
        """Can a logged in user update their profile?"""

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.post("/users/profile", follow_redirects=True, data={
                "username": "updated",
                "email": "updated@email.com",
                "location": "updated location",
                "bio": "updated bio",
                "password" : "password0"
            })

            self.assertEqual(resp.status_code, 200)

            self.assertEqual("updated@email.com", User.query.get(self.user0_id).email)
            self.assertIn("@updated", str(resp.data))
            self.assertIn("updated bio", str(resp.data))
            self.assertIn("updated location", str(resp.data))

    def test_user_delete(self):
        """Can a user delete their profile?"""

        self.assertEqual(len(User.query.all()), 4)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            c.post("/users/delete", follow_redirects=True)

            self.assertEqual(User.query.get(self.user0_id), None)
            self.assertEqual(len(User.query.all()), 3)

    def test_not_logged_in_user_delete(self):
        """Not logged in user trying to delete profile should
           return unauthorized redirect to 200 access unauthorized"""

        with self.client as c:

            resp = c.post("/users/delete", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_user_likes_message(self):
        """Can a user like a message"""

        msg_id = 1000001
        msg = Message(id=msg_id, text="test message", user_id=self.user0_id)

        db.session.add(msg)
        db.session.commit()

        self.assertEqual(len(self.user0.liked_messages), 0)

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            c.post(f"/messages/{msg_id}/like", follow_redirects=True)

            self.assertEqual(len(User.query.get(self.user0_id).liked_messages), 1)

    def test_not_logged_in_user_like(self):
        """Not logged in user should be redirected trying to like a messag
           should unauthorized redirect to 200 access unauthorized"""

        msg = Message(text="test message", user_id=self.user0_id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:

            resp = c.post(f"/messages/{msg.id}/like", follow_redirects=True)

            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_user_likes_page(self):
        """Does a user's liked messages show up?"""

        msg = Message(text="test message", user_id=self.user0_id)

        self.user0.liked_messages.append(msg)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            resp = c.get(f"/users/{self.user0_id}/likes")

            self.assertIn("test message", str(resp.data))
            self.assertIn("test0", str(resp.data))
