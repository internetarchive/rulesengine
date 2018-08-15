import timeit

from django.core.management.base import BaseCommand

from rules.utils.surt import Surt
from rules.utils.tree import tree_for_surt
from rules.views import tree


class Command(BaseCommand):
    help = 'Performs basic benchmarks against the application.'

    def handle(self, *args, **kwargs):
        result = {}

        t = timeit.Timer(
            lambda: tree(None, 'http://(com,example)/foo'))
        result['tree view - http://(com,example)/foo'] = t.timeit(
            number=1000)
        t = timeit.Timer(
            lambda: tree_for_surt(Surt('http://(com,example)/foo')))
        result['tree_for_surt - http://(com,example)/foo'] = t.timeit(
            number=1000)

        print('{:>50}  {}'.format('Test (1000x)', 'Avg. execution time (ms)'))
        print('-' * 80)
        for k, v in result.items():
            print("{:>50}  {}".format(k, result[k]))
