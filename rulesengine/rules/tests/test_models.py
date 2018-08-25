from datetime import (
    datetime,
    timezone,
)

from django.test import TestCase

from rules.models import (
    Rule,
    RuleBase,
    RuleChange,
)


class RuleBaseTestCase(TestCase):

    def test_populate(self):
        now = datetime.now()
        base = RuleBase()
        base.populate({
            'policy': 'block',
            'surt': '(org,',
            'neg_surt': '(org,archive,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
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
        self.assertEqual(base.policy, 'block')
        self.assertEqual(base.surt, '(org,')
        self.assertEqual(base.neg_surt, '(org,archive,')
        self.assertEqual(base.capture_date_start, now)
        self.assertEqual(base.capture_date_end, now)
        self.assertEqual(base.retrieve_date_start, now)
        self.assertEqual(base.retrieve_date_end, now)
        self.assertEqual(base.seconds_since_capture, 256)
        self.assertEqual(base.collection, 'Planets')
        self.assertEqual(base.partner, 'Holst')
        self.assertEqual(base.warc_match, 'jupiter')
        self.assertEqual(base.rewrite_from, 'zeus')
        self.assertEqual(base.rewrite_to, 'jupiter')
        self.assertEqual(base.public_comment, 'initial creation')
        self.assertEqual(base.private_comment, 'going roman')
        self.assertEqual(base.enabled, True)

    def test_populate_no_dates(self):
        base = RuleBase()
        base.populate({
            'policy': 'block',
            'surt': '(org,',
            'neg_surt': '(org,archive,',
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
        self.assertEqual(base.capture_date_start, None)
        self.assertEqual(base.capture_date_end, None)
        self.assertEqual(base.retrieve_date_start, None)
        self.assertEqual(base.retrieve_date_end, None)


class RuleTestCase(TestCase):

    def test_summary(self):
        now = datetime.now()
        rule = Rule()
        rule.populate({
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
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
        self.assertEqual(rule.summary(), {
            'id': None,  # The rule wasn't saved, so this won't be populated.
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'seconds_since_capture': 256,
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'public_comment': 'initial creation',
            'enabled': True,
        })

    def test_full_values(self):
        now = datetime.now()
        rule = Rule()
        rule.populate({
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
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
        self.assertEqual(rule.full_values(), {
            'id': None,  # The rule wasn't saved, so this won't be populated.
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
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

    def test_save_adds_rule_change(self):
        now = datetime.now(timezone.utc)
        rule = Rule()
        rule.populate({
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
            },
            'retrieve_date': {
                'start': now.isoformat(),
                'end': now.isoformat(),
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
        rule.save()
        last_change = RuleChange.objects.all().order_by('-pk')[0]
        self.assertEqual(last_change.change_type, 'c')
        rule.policy = 'allow'
        rule.save()
        last_change = RuleChange.objects.all().order_by('-pk')[0]
        self.assertEqual(last_change.change_type, 'u')
        self.assertEqual(last_change.policy, 'block')

    def test_str(self):
        rule = Rule(
            policy='block',
            surt='(org,')
        self.assertEqual(str(rule), 'BLOCK PLAYBACK ((org,)')


class RuleChangeTestCase(TestCase):

    def setUp(self):
        self.now = datetime.now(timezone.utc)
        self.rule = Rule()
        self.rule_data = {
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': self.now.isoformat(),
                'end': self.now.isoformat(),
            },
            'retrieve_date': {
                'start': self.now.isoformat(),
                'end': self.now.isoformat(),
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
        }
        self.rule.populate(self.rule_data)
        self.rule.save()

    def test_summary(self):
        change = RuleChange(
            rule=self.rule,
            change_date=self.now,
            change_user='Gustav Holst',
            change_comment='composed',
            change_type='c')
        self.assertEqual(change.change_summary(), {
            'id': None,
            'rule_id': self.rule.id,
            'date': self.now,
            'user': 'Gustav Holst',
            'comment': 'composed',
            'type': 'created',
        })

    def test_full_change(self):
        self.maxDiff = None
        change = RuleChange(
            rule=self.rule,
            change_date=self.now,
            change_user='Gustav Holst',
            change_comment='composed',
            change_type='c')
        change.populate({
            'policy': 'block',
            'surt': '(org,',
            'capture_date': {
                'start': self.now.isoformat(),
                'end': self.now.isoformat(),
            },
            'retrieve_date': {
                'start': self.now.isoformat(),
                'end': self.now.isoformat(),
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
        self.assertEqual(change.full_change(), {
            'id': None,
            'rule_id': self.rule.id,
            'date': self.now,
            'user': 'Gustav Holst',
            'comment': 'composed',
            'type': 'created',
            'rule': {
                'id': None,
                'policy': 'block',
                'surt': '(org,',
                'capture_date': {
                    'start': self.now.isoformat(),
                    'end': self.now.isoformat(),
                },
                'retrieve_date': {
                    'start': self.now.isoformat(),
                    'end': self.now.isoformat(),
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
            },
        })
