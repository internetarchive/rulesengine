import datetime
import os
import random
import sys

from django.core.management.base import BaseCommand

from rules.models import Rule
from rules.utils.validators import POLICY_CHOICES


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
        # Require the user to go through a step before fuzzing the database.
        if os.environ.get(self.UNDERSTOOD) != 'understood':
            self.stderr.write(
                'This command adds fuzzed data to the database, no matter '
                'the environment!')
            self.stderr.write(
                'Please run this command with the environment variable ' +
                self.UNDERSTOOD + ' set to the value `understood`.')
            sys.exit(1)
        # Generate the requested number of unique SURTs.
        surts = []
        while len(surts) < kwargs['records'][0]:
            surt = self.build_surt()
            if surt not in surts:
                surts.append(surt)
                self.stdout.write('{}: {}'.format(len(surts), surt))
        # Generate and save a rule for each SURT.
        for surt in surts:
            rule = Rule(surt=surt)
            self.add_constraints(rule)
            rule.save()

    def build_surt(self):
        """Builds a SURT with varying complexity."""
        surt = '{}://('.format(random.choice(self.SCHEMATA))
        # 1 in 10 chance it's just a protocol. Otherwise, add a domain.
        if random.randint(1, 10) != 1:
            surt = self.add_domain(surt)
        return surt

    def add_domain(self, surt):
        """Builds a domain with varying complexity."""
        surt += random.choice(self.TLDs)
        domain_chance = random.randint(0, 10)
        # 1 in 10 chance it's just a TLD
        if domain_chance == 1:
            return surt
        # Add an authority.
        surt += random.choice(self.DOMAINS)
        # 2 in 10 chance for 1-3 subdomains.
        if domain_chance > 8:
            for i in range(0, random.randint(1, 3)):
                surt += 'sub,'
        # 6 in 10 chance for a closing paren and path.
        if domain_chance > 3:
            surt += ')'
            surt = self.add_path(surt)
        return surt

    def add_path(self, surt):
        """Builds a path with varying complexity."""
        # 2 in 3 chance of adding a random number of path elements
        if random.randint(1, 3) < 3:
            for i in range(0, random.randint(1, 3)):
                surt += '/path'
        # 1 in 3 chance for a query string.
        if random.randint(1, 3) == 1:
            surt = self.add_query(surt)
        # 1 in 6 chance for a fragment.
        if random.randint(1, 6) == 1:
            surt = self.add_fragment(surt)
        return surt

    def add_query(self, surt):
        """Builds a query string with varying complexity."""
        surt += '?'
        surt += '&'.join(
            ['key{}=val{}'.format(i, i) for i in range(random.randint(1, 3))])
        return surt

    def add_fragment(self, surt):
        """Builds a random fragment."""
        surt += '#hash{}'.format(random.randint(1, 10))
        return surt

    def add_constraints(self, rule):
        """Adds random constraints to the rule."""
        # Sets a random policy.
        rule.policy = random.choice(POLICY_CHOICES)[0]
        # 1 in 2 chance of restriction by capture date.
        if random.randint(1, 2) == 1:
            rule.capture_date_start = self.NOW
            rule.capture_date_end = self.ONE_YEAR
        # 1 in 3 chance of restriction by retrieval date.
        if random.randint(1, 3) == 1:
            rule.retrieve_date_start = self.NOW
            rule.retrieve_date_end = self.ONE_YEAR
        # 1 in 5 chance of 1 year embargo.
        if random.randint(1, 5) == 1:
            rule.seconds_since_capture = 3600 * 24 * 365
        # 1 in 10 chance of restriction by collection and partner.
        if random.randint(1, 10) == 1:
            rule.collection = 'collection {}'.format(random.randint(1, 3))
            rule.partner = 'partner {}'.format(random.randint(1, 3))
        # 1 in 10 chance of restriction on WARC name.
        if random.randint(1, 10) == 1:
            rule.warc_match = 'warc {}\\d+'.format(random.randint(1, 3))
        # If rule policy involves rewriting, add from/to values.
        if rule.policy in ('rewrite-all', 'rewrite-js', 'rewrite-headers'):
            rule.rewrite_from = 'from {}'.format(random.randint(1, 3))
            rule.rewrite_to = 'to {}'.format(random.randint(1, 3))
        # 1 in 3 chance of public comment.
        if random.randint(1, 3) == 1:
            rule.public_comment = 'public comment {}'.format(
                random.randint(1, 3))
        # 1 in 2 chance of private comment.
        if random.randint(1, 2) == 1:
            rule.private_comment = 'private comment {}'.format(
                random.randint(1, 3))
        # 1 in 5 chance of rule being disabled.
        if random.randint(1, 5) == 1:
            rule.enabled = False
