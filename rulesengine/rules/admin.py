
import re
from functools import lru_cache

import urlcanon
from django.contrib import admin
from django.db import connection
from django.db.models import Q

from .models import (
    Rule,
    RuleChange
)

SEARCH_TERM_REGEX = re.compile(r'^(?:(?P<protocol>\w+)://)?(?P<rest>.*)$')

# TODO - flush cache on any rule addition or modification
@lru_cache(maxsize=1)
def get_surt_part_tree():
    """Return a tree-like representation of the all rule SURTs as a dict with
    protocol and SURT part keys.

    Example:
    {
      '': {
        'gov': {
          'cdc': {
            'www2': {},
            'www1': {},
          },
          'nih': {
            'www'
          }
        }
      },
      'http': { 'gov': { ... }, ... },
      'https': { 'gov': { ... }, ... },
      ...
    }

    """
    cur = connection.cursor()
    cur.execute("select protocol, split_part(surt, ')', 1) _surt from rules_rule "
                "group by protocol, _surt")
    res = cur.fetchall()
    surt_part_tree = {}
    for protocol, surt in res:
        d = surt_part_tree
        for k in [protocol] + surt.split(','):
            if k not in d:
                d[k] = {}
            d = d[k]
    return surt_part_tree

# Register your models here.
class RuleAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "protocol",
        "surt",
        "collection",
        "partner",
        "capture_date_start",
        "capture_date_end",
        "enabled"
    )
    list_filter = ("enabled", "partner", "collection")
    search_fields = ("surt",)

    def get_search_results(self, request, queryset, search_term):
        """Define a custom search handler that automatically converts a
        URL input to a SURT.
        """
        match_d = SEARCH_TERM_REGEX.match(search_term).groupdict()
        protocol = match_d['protocol']
        rest = match_d['rest']

        # Use the absence of a period in the substring preceeding the first
        # slash to detect that path is a surt
        if '.' not in rest.split('/', 1)[0]:
            # rest is a SURT.
            surt = rest.lstrip('(')
            # Remove any trailing comma for compatibility with rule specifications.
            splits = surt.split(')', 1)
            splits[0] = splits[0].rstrip(',')
            surt = ')'.join(splits)
        else:
            # search_term is a URL, so get the SURT.
            # If the search_term specifies no protocol, prepend one for uniformity
            # of parsing.
            parsed = urlcanon.parse_url(
                search_term if protocol else 'http://{}'.format(search_term)
            )
            # Add a trailing slash if necessary to get ensure that the resulting
            # SURT includes it.
            parsed.path = parsed.path or b'/'
            # Exclude the scheme and trailing comma from the SURT.
            surt = parsed.surt(with_scheme=False, trailing_comma=False)\
                         .decode('utf-8')

        # Add the surt_part_tree to the request object.
        request.surt_part_tree = get_surt_part_tree()
        # Add a list of (<current-surt-part>, <all-surt-tree-options>) tuples
        # as used by the surt-part-navigator element to the request object.
        request.surt_part_options_tuples = []
        d = request.surt_part_tree
        for part in [protocol] + surt.split(')', 1)[0].split(','):
            request.surt_part_options_tuples.append((part, sorted(d.keys())))
            d = d[part]
        # Add a final default-empty pair that list any available, immediate
        # descendants.
        if d:
            request.surt_part_options_tuples.append(
                ('', [''] + sorted(d.keys()))
            )

        # Create a surt query for both verbatim and wildcard matches.
        surt_query = Q(surt=surt) | Q(surt=surt + '%')

        if protocol is None:
            # Protocol was not specified, so search for rules with a similarly
            # unspecified protocol and matching surt.
            queryset = queryset.filter(Q(protocol=None) & surt_query)
        else:
            # Protocol was specified, so search for both:
            # - rules that specify this protocol and a wildcard surt (i.e. '%')
            # - rules that specify this protocol and match the surt query.
            protocol_lower = protocol.lower()
            queryset = queryset.filter(
                (Q(protocol=protocol_lower) & Q(surt='%'))
                | (
                    (Q(protocol__isnull=True) | Q(protocol=protocol_lower))
                    & surt_query
                )
            )

        # Order by surt specificity descending.
        queryset = queryset.order_by(
            '-protocol',
            '-surt',
            'policy',
            'capture_date_start',
            'capture_date_end',
        )

        may_have_duplicates = False
        return queryset, may_have_duplicates

admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleChange)
