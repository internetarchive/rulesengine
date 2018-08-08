from django.test import TestCase


class NothingTestCase(TestCase):

    def test_addition(self):
        self.assertEqual(1 + 1, 2)
