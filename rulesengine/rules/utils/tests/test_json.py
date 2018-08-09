from datetime import datetime
import unittest

from rules.utils import json


class JSONTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = {
            'start_date': datetime(1963, 11, 23, 17, 16, 20),
            'companions': [
                'Rose',
                'Mickey',
                'Donna',
            ],
            'enemies': [
                'The Master',
                'Daleks',
                'Cybermen',
            ],
        }

    def test_success(self):
        response = json.success(self.obj)
        self.assertEqual(
            response.content.decode(),
            '{"status": "success", "message": "ok", "result": {"start_date":'
            ' "1963-11-23T17:16:20", "companions": ["Rose", "Mickey", "Donna"]'
            ', "enemies": ["The Master", "Daleks", "Cybermen"]}}')

    def test_error(self):
        response = json.error("dalek", None)
        self.assertEqual(
            response.content.decode(),
            '{"status": "error", "message": "dalek"}')

    def test_error_with_obj(self):
        response = json.error("dalek", {'exterminate': True})
        self.assertEqual(
            response.content.decode(),
            '{"status": "error", "message": "dalek", "result": {"exterminate"'
            ': true}}')
