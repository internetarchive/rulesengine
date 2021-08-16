import timeit

from django.core.management.base import BaseCommand

from rules.views import rules_for_surt as rules_view


class Command(BaseCommand):
    help = 'Performs basic benchmarks against the application.'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            '{:>50}  {}'.format('Test (1000x)', 'Avg. execution time (ms)'))
        self.stdout.write('-'*80)

        t = timeit.Timer(
            lambda: rules_view(None, 'com,example0)/path'))
        self.stdout.write('{:>50}  {}'.format(
            'rules view - http://(com,example0)/path',
            t.timeit(number=1000)))
