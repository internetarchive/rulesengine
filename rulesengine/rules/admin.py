
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

SEARCH_TERM_REGEX = re.compile(r'^(?:(?P<protocol>\w+))?://(?P<rest>.*)$')

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
    cur.execute("select protocol, split_part(surt, ')', 1) _surt from "
                "rules_rule group by protocol, _surt")
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

    # Rope in the custom CSS and JS.
    class Media:
        css = {
            "all": ("rule-admin.css",)
        }
        js = ("rule-admin.js",)

    def _parse_search_term(self, search_term):
        """Parse the search term and return a (<protocol>, <surt>) tuple, where
        surt may be None, or raise a ValueError if parsing fails.
        """
        match_d = SEARCH_TERM_REGEX.match(search_term).groupdict()
        if not match_d:
            raise ValueError
        # Use an empty string for an unspecified protocol to match the rule
        # specification format.
        protocol = match_d['protocol'] or ''
        rest = match_d['rest']
        if not rest:
            return protocol, None

        if rest[0] == '(':
            # rest is a SURT.
            surt = rest.lstrip('(')
            # Remove any trailing comma for compatibility with rule
            # specifications.
            splits = surt.split(')', 1)
            splits[0] = splits[0].rstrip(',')
            surt = ')'.join(splits)
            return protocol, surt

        # search_term is a URL, so get the SURT.
        # If the search_term specifies no protocol, prepend one for
        # uniformity of parsing.
        parsed = urlcanon.parse_url(
            search_term if protocol else 'http://{}'.format(search_term)
        )
        # Add a trailing slash if necessary to get ensure that the
        # resulting SURT includes it.
        parsed.path = parsed.path or b'/'
        # Exclude the scheme and trailing comma from the SURT.
        surt = parsed.surt(with_scheme=False, trailing_comma=False)\
                     .decode('utf-8')
        return protocol, surt

    def _get_surt_part_options_tuples(self, surt_part_tree, protocol, surt):
        """Return an ordered list of (<current-surt-part>,
        <all-surt-tree-part-options>) for the current search.
        """
        surt_part_options_tuples = []
        d = surt_part_tree
        # Always include the protocol selector.
        surt_part_options_tuples.append((protocol, sorted(d.keys())))
        d = d[protocol]
        if surt != ')/':
            for part in surt.split(')', 1)[0].split(','):
                surt_part_options_tuples.append((part, sorted(d.keys())))
                if part in d:
                    d = d[part]
                else:
                    # If part does not exist in the surt_part_tree dict, pop
                    # the last options tuple so that it's subsequently,
                    # correctly added as a next-direct-descendant selector and
                    # do break.
                    surt_part_options_tuples.pop()
                    break
        # Add a final default-empty pair that list any available, immediate
        # descendants.
        if d:
            surt_part_options_tuples.append(('', [''] + sorted(d.keys())))

        return surt_part_options_tuples

    def _build_surt_query(self, surt):
        # Match on any rule for which this surt is prefix of its surt.
        # Maybe this is too loose a match and should be behind a flag?
        surt_query = Q(surt__startswith=surt)

        # Note that the above prefix match replaces the following logic with
        # maybe we want to reinstate with the looser, prefix match behind a
        # flag?
        #
        # # Match on verbatim surt or verbatim surt with trailing wildcard.
        # surt_query = Q(surt=surt) | Q(surt=surt + '%')

        # # If SURT not closed, match on closed version and closed version with
        # # trailing wildcard.
        # if ')/' not in surt:
        #     surt_query |= Q(surt=surt + ')/')
        #     surt_query |= Q(surt=surt + ')/%')

        # Match on any prefix part with a trailing wildcard.
        surt_query |= Q(surt='%')
        query_parts = []
        for part in surt.split(','):
            query_parts.append(part)
            surt_query |= Q(surt=','.join(query_parts) + '%')

        return surt_query

    def changelist_view(self, request, extra_context=None):
        """Adapted from: https://stackoverflow.com/a/8494985
        Pop custom URL args out of the request and put them in extra_context
        to prevent Django from throwing a fit and redirecting to ...?e=1
        """
        self.custom_search_fields = {}
        request.GET._mutable=True
        for k in tuple(request.GET.keys()):
            if k != 'q':
                # Note that the pop() method return a list.
                self.custom_search_fields[k] = request.GET.pop(k)
        request.GET_mutable=False
        return super().changelist_view(request)

    def get_search_results(self, request, queryset, search_term):
        """Define a custom search handler that automatically converts a
        URL input to a SURT.
        """
        # We don't expect these search results to include duplicates, so
        # specify that here to make the return expressions more explicit.
        MAY_HAVE_DUPLICATES = False

        # Add the surt_part_tree to the request object.
        surt_part_tree = get_surt_part_tree()
        request.surt_part_tree = surt_part_tree

        # Order by surt specificity descending.
        queryset = queryset.order_by(
            '-protocol',
            '-surt',
            'policy',
            'capture_date_start',
            'capture_date_end',
        )

        # if no search was specified, return the default queryset.
        if search_term == '':
            request.surt_part_options_tuples = (
                ('', sorted(request.surt_part_tree.keys())),
            )
            return queryset, MAY_HAVE_DUPLICATES

        # Parse the search term.
        protocol, surt = self._parse_search_term(search_term)

        # Get the surt nav option tuples.
        request.surt_part_options_tuples = \
            self._get_surt_part_options_tuples(surt_part_tree, protocol, surt)

        # Create a surt query for both verbatim and wildcard matches.
        surt_query = self._build_surt_query(surt)

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
                (Q(protocol__isnull=True) | Q(protocol=protocol_lower))
                & surt_query
            )

        return queryset, MAY_HAVE_DUPLICATES

admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleChange)
