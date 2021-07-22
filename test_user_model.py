"""User model tests."""

# run these tests like:
#
#    python -m unittest test_user_model.py


import os
from unittest import TestCase
from sqlalchemy import exc
from models import db, User, Message, Follows

# BEFORE we import our app, let's set an environmental variable
# to use a different database for tests (we need to do this
# before we import our app, since that will have already
# connected to the database

os.environ['DATABASE_URL'] = "postgresql:///warbler_test"

# Now we can import app

from app import app

# Create our tables (we do this here, so we only create the tables
# once for all tests --- in each test, we'll delete the data
# and create fresh new clean test data

db.create_all()


class UserModelTestCase(TestCase):
    """Test views for messages."""

    def setUp(self):
        """Create test client, add sample data."""

        User.query.delete()
        Message.query.delete()
        Follows.query.delete()

        user0 = User(username='test0', email='test0@email.com', password='password0')
        user1 = User(username='test1', email='test1@email.com', password='password1')
        
        user0.id = 100
        user1.id = 101

        db.session.add_all([user0, user1])
        db.session.commit()

        self.user0 = user0
        self.user1 = user1

        self.client = app.test_client()

    def tearDown(self):
        """Rollback db.session"""
        db.session.rollback()

    
    ##### USER TESTS 

    def test_user_model(self):
        """Does basic model work?"""

        u = User(
            email="test@test.com",
            username="testuser",
            password="HASHED_PASSWORD"
        )

        db.session.add(u)
        db.session.commit()

        # User should have no messages & no followers & no liked messagess
        self.assertEqual(len(u.messages), 0)
        self.assertEqual(len(u.followers), 0)
        self.assertEqual(len(u.liked_messages), 0)

    def test_user_repr(self):
        """Does the repr work as intended?"""

        self.assertEqual(self.user0.__repr__(), "<User #100: test0, test0@email.com>")
        self.assertEqual(self.user1.__repr__(), "<User #101: test1, test1@email.com>")

    def test_valid_user_signup(self):
        """Does user signup work as intended?"""

        self.assertEqual(len(User.query.all()), 2)
        
        user2 = User.signup('test2', 'test2@email.com', 'password2', None)

        self.assertEqual(len(User.query.all()), 3)
        self.assertNotEqual(user2.password, 'password2') 
    
    def test_invalid_username_signup(self):
        """Does an invalid username raise an error?"""

        invalid = User.signup(None, 'test2@email.com', 'password2', None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_invalid_password_signup(self):
        """Does an invalid password raise an error?"""
 
        with self.assertRaises(ValueError):
            invalid = User.signup('test2', 'test2@email.com', None, None)


    def test_invalid_email_signup(self):
        """Does an invalid email raise an error?"""

        invalid = User.signup('test2', None, 'password2', None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_existing_username_signup(self):
        """Does signing up with an existing username raise an error?"""

        invalid = User.signup('test0', 'test2@email.com', 'password2', None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_existing_email_signup(self):
        """Does signing up with an existing email raise an error?"""

        invalid = User.signup('test2', 'test0@email.com', 'password2', None)
        with self.assertRaises(exc.IntegrityError):
            db.session.commit()

    def test_user_authentication(self):
        """Does user authentication work"""

        user2 = User.signup('test2', 'test2@email.com', 'password2', None)

        valid = User.authenticate('test2', 'password2')
        self.assertIsNotNone(valid, True)

        invalid_user = User.authenticate('test5', 'password5')
        self.assertEqual(invalid_user, False)
        
        invalid_password = User.authenticate('test2', 'password5')
        self.assertEqual(invalid_password, False)

    #### FOLLOW TESTS
    def test_user_follows(self):
        """Does following work as intended?"""

        self.assertEqual(len(self.user0.following), 0)
        self.assertEqual(len(self.user0.followers), 0)
        self.assertEqual(len(self.user1.following), 0)
        self.assertEqual(len(self.user1.followers), 0)

        self.user0.following.append(self.user1)
        db.session.commit()

        self.assertEqual(len(self.user0.following), 1)
        self.assertEqual(len(self.user0.followers), 0)
        self.assertEqual(len(self.user1.following), 0)
        self.assertEqual(len(self.user1.followers), 1)

    def test_user_is_following(self):
        '''Does {user}.is_following({other_user}) work as intended'''

        self.assertEqual(self.user0.is_following(self.user1), False)
        self.assertEqual(self.user1.is_following(self.user0), False)

        self.user0.following.append(self.user1)
        db.session.commit()

        self.assertEqual(self.user0.is_following(self.user1), True)
        self.assertEqual(self.user1.is_following(self.user0), False)
        

    def test_user_is_followed_by(self):
        '''Does {user}.is_followed_by({other_user}) work as intended'''

        self.assertEqual(self.user0.is_followed_by(self.user1), False)
        self.assertEqual(self.user1.is_followed_by(self.user0), False)

        self.user0.following.append(self.user1)
        db.session.commit()

        self.assertEqual(self.user0.is_followed_by(self.user1), False)
        self.assertEqual(self.user1.is_followed_by(self.user0), True)