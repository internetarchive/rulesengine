from datetime import datetime
from unittest import TestCase

from jsonschema import ValidationError

from rules.utils.validators import validate_rule_json


class ValidateRuleJSONTestCase(TestCase):

    def setUp(self):
        self.now = datetime.now()

    def test_success(self):
        try:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'environment': 'prod',
                'surt': 'http://(',
            })
            validate_rule_json({
                'policy': 'block',
                'surt': '(org,',
                'neg_surt': '(org,archive,',
                'capture_date_start': self.now.isoformat(),
                'capture_date_end': self.now.isoformat(),
                'retrieve_date_start': self.now.isoformat(),
                'retrieve_date_end': self.now.isoformat(),
                'seconds_since_capture': 256,
                'collection': 'Planets',
                'partner': 'Holst',
                'warc_match': 'jupiter',
                'rewrite_from': 'zeus',
                'rewrite_to': 'jupiter',
                'public_comment': 'initial creation',
                'private_comment': 'going roman',
                'enabled': True,
                'environment': 'prod',
            })
        except Exception:
            self.fail('validate_rule_json unexpectedly raised an exception')

    def test_schema_fail(self):
        with self.assertRaises(ValidationError) as context:
            validate_rule_json({})
        self.assertTrue(
            "Failed validating 'required' in schema" in
            str(context.exception))

    def test_date_fail(self):
        self.maxDiff = None
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'environment': 'prod',
                'surt': 'http://(',
                'capture_date': {
                    'start': 'bad-wolf 1',
                    'end': self.now.isoformat(),
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'capture start date',
                ValueError('Unknown string format:', 'bad-wolf 1')))))
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'environment': 'prod',
                'surt': 'http://(',
                'capture_date': {
                    'start': self.now.isoformat(),
                    'end': 'bad-wolf 2',
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'capture end date',
                ValueError('Unknown string format:', 'bad-wolf 2')))))
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'environment': 'prod',
                'surt': 'http://(',
                'retrieve_date': {
                    'start': 'bad-wolf 3',
                    'end': self.now.isoformat(),
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'retrieve start date',
                ValueError('Unknown string format:', 'bad-wolf 3')))))
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'environment': 'prod',
                'surt': 'http://(',
                'retrieve_date': {
                    'start': self.now.isoformat(),
                    'end': 'bad-wolf 4',
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'retrieve end date',
                ValueError('Unknown string format:', 'bad-wolf 4')))))
