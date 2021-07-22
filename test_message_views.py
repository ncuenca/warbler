"""Message View tests."""

# run these tests like:
#
#    FLASK_ENV=production python -m unittest test_message_views.py


import os
from unittest import TestCase

from models import db, connect_db, Message, User

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app, CURR_USER_KEY

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()

# Don't have WTForms use CSRF at all, since it's a pain to test

app.config['WTF_CSRF_ENABLED'] = False


class MessageViewTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()

        self.client = app.test_client()

        self.test_user0 = User.signup(username="user0",
                                    email="test0@test.com",
                                    password="password0",
                                    image_url=None)
        self.test_user1 = User.signup(username="user1",
                                    email="test1@test.com",
                                    password="password1",
                                    image_url=None)
        self.test_user2 = User.signup(username="user2",
                                    email="test2@test.com",
                                    password="password2",
                                    image_url=None)

        self.user0_id = 100000                                
        self.user1_id = 100001                                   
        self.user2_id = 100002

        self.test_user0.id = self.user0_id                                  
        self.test_user1.id = self.user1_id                                  
        self.test_user2.id = self.user2_id                                  

        db.session.commit()

    def test_add_message(self):
        """Can user add a message?"""

        # Since we need to change the session to mimic logging in,
        # we need to use the changing-session trick:

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            # Now, that session setting is saved, so we can have
            # the rest of ours test
            resp = c.post("/messages/new", data={"text": "Hello"})

            # Make sure it redirects
            self.assertEqual(resp.status_code, 302)
            msg = Message.query.one()
            self.assertEqual(msg.text, "Hello")

    def test_not_logged_in_add_message(self):
        """If a user isn't logged in and tries to add a message, 
           response 200 should be returned."""

        with self.client as c:
            resp = c.post("/messages/new", data={"text": "Hello"}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))

    def test_delete_message(self):
        """Can user delete a message?"""

        msg = Message(id=100001, text='delete this', user_id=self.user0_id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            with c.session_transaction() as sess:
                sess[CURR_USER_KEY] = self.user0_id

            self.assertEqual(len(Message.query.all()), 1)

            resp = c.post(f"/messages/100001/delete")

            self.assertEqual(resp.status_code, 302)
            self.assertEqual(len(Message.query.all()), 0)

    def test_not_logged_in_delete_message(self):
        """If a user isn't logged in and tries to delete a message, 
           response 200 should be returned."""
        
        msg = Message(id=100001, text='delete this', user_id=self.user0_id)

        db.session.add(msg)
        db.session.commit()

        with self.client as c:
            resp = c.post(f"/messages/{msg.id}/delete", follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            self.assertIn("Access unauthorized", str(resp.data))
