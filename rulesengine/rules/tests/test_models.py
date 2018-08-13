from datetime import datetime

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
            'date_start': now.isoformat(),
            'date_end': now.isoformat(),
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': 'true',
        })
        self.assertEqual(base.policy, 'block')
        self.assertEqual(base.surt, '(org,')
        self.assertEqual(base.neg_surt, '(org,archive,')
        self.assertEqual(base.date_start, now)
        self.assertEqual(base.date_end, now)
        self.assertEqual(base.collection, 'Planets')
        self.assertEqual(base.partner, 'Holst')
        self.assertEqual(base.warc_match, 'jupiter')
        self.assertEqual(base.rewrite_from, 'zeus')
        self.assertEqual(base.rewrite_to, 'jupiter')
        self.assertEqual(base.who, 'gustav')
        self.assertEqual(base.public_comment, 'initial creation')
        self.assertEqual(base.private_comment, 'going roman')
        self.assertEqual(base.enabled, True)


class RuleTestCase(TestCase):

    def test_summary(self):
        now = datetime.now()
        rule = Rule()
        rule.populate({
            'policy': 'block',
            'surt': '(org,',
            'date_start': now.isoformat(),
            'date_end': now.isoformat(),
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': 'true',
        })
        self.assertEqual(rule.summary(), {
            'id': None,  # The rule wasn't saved, so this won't be populated.
            'policy': 'block',
            'surt': '(org,',
            'neg_surt': '',
            'date_start': now,
            'date_end': now,
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'enabled': True,
        })

    def test_full_values(self):
        now = datetime.now()
        rule = Rule()
        rule.populate({
            'policy': 'block',
            'surt': '(org,',
            'date_start': now.isoformat(),
            'date_end': now.isoformat(),
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': 'true',
        })
        self.assertEqual(rule.full_values(), {
            'id': None,  # The rule wasn't saved, so this won't be populated.
            'policy': 'block',
            'surt': '(org,',
            'neg_surt': '',
            'date_start': now,
            'date_end': now,
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': True,
        })

    def test_str(self):
        rule = Rule(
            policy='block',
            surt='(org,')
        self.assertEqual(str(rule), 'BLOCK PLAYBACK ((org,)')


class RuleChangeTestCase(TestCase):

    def setUp(self):
        self.now = datetime.now()
        self.rule = Rule()
        self.rule_data = {
            'policy': 'block',
            'surt': '(org,',
            'date_start': self.now.isoformat() + 'Z',
            'date_end': self.now.isoformat() + 'Z',
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': 'true',
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
        self.assertEqual(change.summary(), {
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
            'date_start': self.now.isoformat(),
            'date_end': self.now.isoformat(),
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': 'true',
        })
        self.assertEqual(change.full_change(), {
            'id': None,
            'rule_id': self.rule.id,
            'date': self.now,
            'user': 'Gustav Holst',
            'comment': 'composed',
            'type': 'created',
            'policy': 'block',
            'surt': '(org,',
            'neg_surt': '',
            'date_start': self.now,
            'date_end': self.now,
            'collection': 'Planets',
            'partner': 'Holst',
            'warc_match': 'jupiter',
            'rewrite_from': 'zeus',
            'rewrite_to': 'jupiter',
            'who': 'gustav',
            'public_comment': 'initial creation',
            'private_comment': 'going roman',
            'enabled': True,
        })
