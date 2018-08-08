import unittest

from rules.utils.surt import Surt


class SurtTestCase(unittest.TestCase):

    def test_protocol_only(self):
        surt = Surt('http')
        self.assertEqual(surt.parts, ['http://('])
        surt = Surt('http://(')
        self.assertEqual(surt.parts, ['http://('])

    def test_domain_only(self):
        surt = Surt.from_url('https://archive.org')
        self.assertEqual(surt.parts, ['https://(', 'org,', 'archive,)'])
        self.assertEqual(surt.domain_parts, ['org', 'archive'])

    def test_domain_and_path(self):
        surt = Surt.from_url('https://archive.org/about')
        self.assertEqual(surt.parts, [
            'https://(', 'org,', 'archive,)', '/about'])
        surt = Surt.from_url('https://archive.org/about/bios.php')
        self.assertEqual(surt.parts, [
            'https://(', 'org,', 'archive,)', '/about', '/bios.php'])
        self.assertEqual(surt.path_parts, ['about', 'bios.php'])

    def test_domain_and_query(self):
        surt = Surt.from_url('https://example.com?first=rose&last=tyler')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '?first=rose&last=tyler'])

    def test_domain_path_and_query(self):
        surt = Surt.from_url('https://example.com/doctor/companion?name=rose')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '/doctor', '/companion',
            '?name=rose'])

    def test_domain_and_hash(self):
        surt = Surt.from_url('https://example.com/#who')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '#who'])

    def test_domain_path_and_hash(self):
        surt = Surt.from_url('https://example.com/doctor#actors')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '/doctor', '#actors'])

    def test_domain_query_and_hash(self):
        surt = Surt.from_url('https://example.com/?class=show#doctorwho')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '?class=show', '#doctorwho'])

    def test_domain_path_query_and_hash(self):
        surt = Surt.from_url(
            'https://example.com/doctor/companion?name=rose#actress')
        self.assertEqual(surt.parts, [
            'https://(', 'com,', 'example,)', '/doctor', '/companion',
            '?name=rose', '#actress'])

    def test_str(self):
        given = 'http://(org,archive,)'
        surt = Surt(given)
        self.assertEqual(str(surt), given)
