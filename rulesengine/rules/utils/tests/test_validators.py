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
                'surt': 'http://(',
            })
            validate_rule_json({
                'policy': 'block',
                'surt': '(org,',
                'neg_surt': '(org,archive,',
                'capture_date': {
                    'start': self.now.isoformat(),
                    'end': self.now.isoformat(),
                },
                'retrieve_date': {
                    'start': self.now.isoformat(),
                    'end': self.now.isoformat(),
                },
                'ip_range': {
                    'start': '4.4.4.4',
                    'end': '8.8.8.8',
                },
                'seconds_since_capture': 256,
                'collection': 'Planets',
                'partner': 'Holst',
                'warc_match': 'jupiter',
                'rewrite_from': 'zeus',
                'rewrite_to': 'jupiter',
                'public_comment': 'initial creation',
                'private_comment': 'going roman',
                'enabled': True,
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

    def test_ip_range_fail(self):
        self.maxDiff = None
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'surt': 'http://(',
                'ip_range': {
                    'start': 'bad wolf',
                    'end': '8.8.8.8',
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'ip range start',
                ValueError("'bad wolf' does not appear to be an IPv4 or "
                           'IPv6 address')
            ))))
        with self.assertRaises(ValueError) as context:
            validate_rule_json({
                'policy': 'block',
                'enabled': True,
                'surt': 'http://(',
                'ip_range': {
                    'start': '4.4.4.4',
                    'end': 'bad wolf',
                },
            })
        self.assertEqual(
            str(context.exception),
            str(ValueError((
                'ip range end',
                ValueError("'bad wolf' does not appear to be an IPv4 or "
                           'IPv6 address')
            ))))
