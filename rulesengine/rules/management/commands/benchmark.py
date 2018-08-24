import timeit

from django.core.management.base import BaseCommand

from rules.utils.surt import Surt
from rules.utils.tree import tree as tree_func
from rules.views import tree_for_surt as tree_view


class Command(BaseCommand):
    help = 'Performs basic benchmarks against the application.'

    def handle(self, *args, **kwargs):
        self.stdout.write(
            '{:>50}  {}'.format('Test (1000x)', 'Avg. execution time (ms)'))
        self.stdout.write('-'*80)

        t = timeit.Timer(
            lambda: tree_view(None, 'http://(com,example0)/path'))
        self.stdout.write('{:>50}  {}'.format(
            'tree view - http://(com,example0)/path',
            t.timeit(number=1000)))

        t = timeit.Timer(
            lambda: tree_func(Surt('http://(com,example0)/path')))
        self.stdout.write('{:>50}  {}'.format(
            'tree function - http://(com,example0)/path',
            t.timeit(number=1000)))
