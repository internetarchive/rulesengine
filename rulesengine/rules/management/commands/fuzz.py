import datetime
import os
import random
import sys

from django.core.management.base import BaseCommand

from rules.models import Rule


class Command(BaseCommand):
    help = 'Fuzzes data in the database for testing.'

    UNDERSTOOD = 'I_UNDERSTAND_THIS_TOUCHES_THE_DB'
    SCHEMATA = [
        'http',
        'https',
        'ftp',
    ]
    TLDs = [
        'com,',
        'org,',
        'net,',
        'int,',
        'edu,',
        'gov,',
        'mil,',
    ]
    DOMAINS = ['example{},'.format(i) for i in range(0, 10)]
    NOW = datetime.datetime.now(datetime.timezone.utc)
    ONE_YEAR = NOW + datetime.timedelta(days=365)

    def add_arguments(self, parser):
        parser.add_argument('records', nargs=1, type=int)

    def handle(self, *args, **kwargs):
        if os.environ.get(self.UNDERSTOOD) != 'understood':
            self.stderr.write(
                'This command adds fuzzed data to the database, no matter '
                'the environment!')
            self.stderr.write(
                'Please run this command with the environment variable ' +
                self.UNDERSTOOD + ' set to the value `understood`.')
            sys.exit(1)
        surts = []
        while len(surts) < kwargs['records'][0]:
            surt = self.build_surt()
            if surt not in surts:
                surts.append(surt)
        for surt in surts:
            rule = Rule(surt=surt)
            self.add_constraints(rule)
            rule.save()

    def build_surt(self):
        surt = '{}://('.format(random.choice(self.SCHEMATA))
        if random.randint(0, 10) > 0:
            surt = self.add_domain(surt)
        return surt

    def add_domain(self, surt):
        surt += random.choice(self.TLDs)
        domain_chance = random.randint(0, 10)
        if domain_chance > 1:
            surt += random.choice(self.DOMAINS)
        if domain_chance > 8:
            for i in range(0, random.randint(1, 3)):
                surt += 'sub,'
        if domain_chance > 3:
            surt += ')'
            surt = self.add_path(surt)
        return surt

    def add_path(self, surt):
        if random.randint(0, 5) < 4:
            for i in range(0, random.randint(1, 3)):
                surt += '/path'
        if random.randint(0, 5) < 2:
            surt = self.add_query(surt)
        if random.randint(0, 5) == 0:
            surt = self.add_fragment(surt)
        return surt

    def add_query(self, surt):
        surt += '?'
        surt += '&'.join(
            ['key{}=val{}'.format(i, i) for i in range(random.randint(1, 3))])
        return surt

    def add_fragment(self, surt):
        surt += '#hash{}'.format(random.randint(1, 10))
        return surt

    def add_constraints(self, rule):
        rule.policy = random.choice(Rule.POLICY_CHOICES)[0]
        if random.randint(1, 2) == 1:
            rule.capture_date_start = self.NOW
            rule.capture_date_end = self.ONE_YEAR
        if random.randint(1, 3) == 1:
            rule.retrieve_date_start = self.NOW
            rule.retrieve_date_end = self.ONE_YEAR
        if random.randint(1, 5) == 1:
            rule.seconds_since_capture = 3600 * 24 * 365
        if random.randint(1, 10) == 1:
            rule.collection = 'collection {}'.format(random.randint(1, 3))
            rule.partner = 'partner {}'.format(random.randint(1, 3))
        if random.randint(1, 10) == 1:
            rule.warc_match = 'warc {}\\d+'.format(random.randint(1, 3))
        if rule.policy in ('rewrite-all', 'rewrite-js', 'rewrite-headers'):
            rule.rewrite_from = 'from {}'.format(random.randint(1, 3))
            rule.rewrite_to = 'to {}'.format(random.randint(1, 3))
        if random.randint(1, 3) == 1:
            rule.public_comment = 'public comment {}'.format(
                random.randint(1, 3))
        if random.randint(1, 2) == 1:
            rule.private_comment = 'private comment {}'.format(
                random.randint(1, 3))
        if random.randint(1, 5) == 1:
            rule.enabled = False
