import datetime
import unittest

from app.utils import password_from_date


class PasswordFromDateTestCase(unittest.TestCase):
    def test_(self):
        self.assertEqual(password_from_date(datetime.date(2018, 1, 1)), '01012018')
        self.assertEqual(password_from_date(datetime.date(1992, 11, 24)), '24111992')
