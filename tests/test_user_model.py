import unittest

from app.models import SystemUser


class UserModelTestCase(unittest.TestCase):
    def test_password_setter(self):
        u = SystemUser(password='fish')
        self.assertTrue(u.password_hash is not None)

    def test_no_password_getter(self):
        u = SystemUser(password='fish')
        with self.assertRaises(AttributeError):
            u.password()

    def test_password_verification(self):
        u = SystemUser(password='fish')
        self.assertTrue(u.verify_password('fish'))
        self.assertFalse(u.verify_password('anth'))

    def test_password_salt_are_random(self):
        u1 = SystemUser(password='fish')
        u2 = SystemUser(password='fish')
        self.assertTrue(u1.password_hash != u2.password_hash)
