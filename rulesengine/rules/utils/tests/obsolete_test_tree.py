from datetime import (
    datetime,
    timezone,
)

from django.test import TestCase

from rules.utils.surt import Surt
from rules.utils.tree import tree


class TreeTestCase(TestCase):

    fixtures = ["tree-tests.json"]

    def test_surt_only(self):
        results = [str(rule) for rule in tree(Surt("https://(com,example,)/blocked"))]
        self.assertEqual(
            results,
            [
                "ALLOW PLAYBACK (https://()",
                "ALLOW PLAYBACK (https://(com,example,)",
                "BLOCK PLAYBACK (https://(com,example,))",
                "BLOCK PLAYBACK (https://(com,example,)/blocked)",
            ],
        )

    def test_neg_surt(self):
        # XXX Requirements around neg_surt are not yet firmly defined.
        results = [
            str(rule)
            for rule in tree(
                Surt("https://(com,example,)/blocked"), neg_surt="https://("
            )
        ]
        self.assertEqual(results, [])

    def test_collection(self):
        results = [
            str(rule)
            for rule in tree(
                Surt("https://(com,example,)/collection"), collection="collection"
            )
        ]
        self.assertEqual(
            results, ["BLOCK PLAYBACK (https://(com,example,)/collection)"]
        )

    def test_partner(self):
        results = [
            str(rule)
            for rule in tree(Surt("https://(com,example,)/partner"), partner="partner")
        ]
        self.assertEqual(results, ["BLOCK PLAYBACK (https://(com,example,)/partner)"])

    def test_capture_date(self):
        # The following rule blocks content on April Fool's Day
        date = datetime(2018, 4, 1, 12, 0, 0, 0, timezone.utc)
        results = [
            str(rule)
            for rule in tree(Surt("https://(com,example,)/blocked"), capture_date=date)
        ]
        self.assertEqual(results, ["BLOCK PLAYBACK (https://(com,example,))"])
