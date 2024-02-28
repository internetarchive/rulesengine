from datetime import datetime
import unittest

import json

import rules.utils.json


class JSONTestCase(unittest.TestCase):

    def setUp(self):
        self.obj = {
            "start_date": datetime(1963, 11, 23, 17, 16, 20),
            "companions": [
                "Rose",
                "Mickey",
                "Donna",
            ],
            "enemies": [
                "The Master",
                "Daleks",
                "Cybermen",
            ],
        }

    def test_success(self):
        response = rules.utils.json.success(self.obj)
        expected = {
            "status": "success",
            "message": "ok",
            "result": {
                "start_date": "1963-11-23T17:16:20Z",
                "companions": [
                    "Rose",
                    "Mickey",
                    "Donna",
                ],
                "enemies": [
                    "The Master",
                    "Daleks",
                    "Cybermen",
                ],
            },
        }
        self.assertEqual(json.loads(response.content.decode()), expected)

    def test_error(self):
        response = rules.utils.json.error("dalek", None)
        expected = {"status": "error", "message": "dalek"}
        self.assertEqual(json.loads(response.content.decode()), expected)

    def test_error_with_obj(self):
        response = rules.utils.json.error("dalek", {"exterminate": True})
        expected = {
            "status": "error",
            "message": "dalek",
            "result": {"exterminate": True},
        }
        self.assertEqual(json.loads(response.content.decode()), expected)
