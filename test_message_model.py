"""Message model tests."""


import os
from unittest import TestCase
from models import db, User, Message, Follows

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

from app import app

db.create_all()


class MessageModelTestCase(TestCase):
    """Test models for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user0 = User.signup(
                            username='test0', 
                            email='test0@email.com', 
                            password='password0',
                            image_url=None)

        db.session.commit()

        msg0 = Message(
            text="test message0",
            user_id=user0.id,
        )

        db.session.add(msg0)
        db.session.commit()

        self.user0 = user0
        self.msg0 = msg0

        self.client = app.test_client()

    def tearDown(self):
        """Rollback db.session"""
        db.session.rollback()

    
    ##### MESSAGE TESTS 

    def test_message_model(self):
        """Does basic message model work?"""

        self.assertEqual(len(self.user0.messages), 1)

        msg1 = Message(
            text="test message1",
            user_id=self.user0.id,
        )

        db.session.add(msg1)
        db.session.commit()

        self.assertEqual(len(msg1.liked_by), 0)
        self.assertEqual(len(self.user0.messages), 2)

    def test_user_liking_message(self):
        """Does the user/message liking relationship work?"""

        self.assertEqual(len(self.msg0.liked_by), 0)
        self.assertEqual(len(self.user0.liked_messages), 0)

        self.user0.liked_messages.append(self.msg0)
        db.session.commit()

        self.assertEqual(len(self.msg0.liked_by), 1)
        self.assertEqual(len(self.user0.liked_messages), 1)

        # Tests {msg}.is_liked_by({user}) function
        self.assertEqual(self.msg0.is_liked_by(self.user0), True)
