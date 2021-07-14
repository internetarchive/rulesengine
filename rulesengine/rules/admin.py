"""
TODO - Error URLs

http://rulesengine-local:8080/admin/rules/rule/?q=%3A%2F%2F(com%2Cyoutube)%2Fwatch%3Fv%3Dnz2x22z8en4%26feature%3Drelated%25&type=Match

"""

import re
from datetime import datetime
from functools import lru_cache

import urlcanon
from django.contrib import admin
from django.db import connection
from django.db.models import Q

from .models import (
    Rule,
    RuleChange
)

strptime = datetime.strptime

SEARCH_TERM_REGEX = re.compile(r'^(?:(?P<protocol>\w+)?://)?(?P<rest>.*)$')

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

def safe_parse(parser):
    """Return a function that attempts to apply a parser and returns None in
    the event of any exception.
    """
    def f(x):
        try:
            return parser(x)
        except:
            return None
    return f

# Register your models here.
class RuleAdmin(admin.ModelAdmin):
    list_display = (
        "policy",
        "enabled",
        "protocol",
        "surt",
        "neg_surt",
        "collection",
        "partner",
        "rewrite_from",
        "rewrite_to",
        "warc_match",
        "capture_date_start",
        "capture_date_end",
        'retrieve_date_start',
        'retrieve_date_end',
        'seconds_since_capture',
        "ip_range_start",
        "ip_range_end",
        "private_comment",
        "public_comment",
        "environment",
    )
    search_fields = ("surt",)
    custom_search_param_parser_map = {
        'type': safe_parse(str),
        'capture_date': safe_parse(lambda x: strptime(x, '%Y-%m-%d')),
        'capture_time': safe_parse(lambda x: strptime(x, '%H:%M')),
    }

    # Rope in the custom CSS and JS.
    class Media:
        css = {
            "all": ("rule-admin.css",)
        }
        js = ("rule-admin.js",)

    def __init__(self, *args, **kwargs):
        """Define a custom init to add an custom_context property.
        """
        super().__init__(*args, **kwargs)
        self.custom_context = {
            'search_errors': [],
            'search_warnings': [],
        }

    def _parse_search_term(self, search_term):
        """Parse the search term and return a (<protocol>, <surt>) tuple, where
        surt may be None, or raise a ValueError if parsing fails.
        """
        match = SEARCH_TERM_REGEX.match(search_term)
        if not match:
            raise ValueError
        match_d = match.groupdict()
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
        if surt is not None and surt != ')/':
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

    def changelist_view(self, request, extra_context=None):
        """Adapted from: https://stackoverflow.com/a/8494985
        Pop custom URL args out of the request and put them in custom_context
        to prevent Django from throwing a fit and redirecting to ...?e=1
        """
        # Take this opportunity to clear any previous search errors/warnings.
        self.custom_context['search_errors'].clear()
        self.custom_context['search_warnings'].clear()
        # Pop the custom search params from GET.
        request.GET._mutable=True
        for k, parser in self.custom_search_param_parser_map.items():
            value = request.GET.pop(k)[0] if k in request.GET else None
            # Save the original string.
            self.custom_context['{}_orig'.format(k)] = value
            # Parse and save
            self.custom_context[k] = parser(value)
        request.GET_mutable=False
        response = super().changelist_view(
            request,
            extra_context=extra_context
        )
        # Attach custom context to the cl (changelist) object in order to make
        # it available in the template (e.g. search form error) because no
        # amount of messing around with the Django-native extra_context
        # argument seems to work.
        response.context_data['cl'].custom_context = self.custom_context
        return response

    def get_search_results(self, request, queryset, search_term):
        """Define a custom search handler that automatically converts a
        URL input to a SURT.
        """
        # We don't expect these search results to include duplicates, so
        # specify that here to make the return expressions more explicit.
        MAY_HAVE_DUPLICATES = False

        # Add the surt_part_tree to the request object.
        surt_part_tree = get_surt_part_tree()
        self.custom_context['surt_part_tree'] = surt_part_tree

        # Order by surt specificity descending.
        queryset = queryset.order_by(
            '-surt',
            '-protocol',
            'policy',
            'capture_date_start',
            'capture_date_end',
        )

        # If no search was specified, return the default queryset.
        if search_term == '':
            self.custom_context['surt_part_options_tuples'] = \
                self._get_surt_part_options_tuples(surt_part_tree, '', None)
            return queryset, MAY_HAVE_DUPLICATES

        # Attempt to parse the search term.
        try:
            protocol, surt = self._parse_search_term(search_term)
        except ValueError:
            self.custom_context['search_errors'].append(
                '"{}" is not a valid URL or SURT'.format(search_term)
            )
            return queryset, MAY_HAVE_DUPLICATES

        # If no surt was specified, return the default queryset.
        if not surt:
            self.custom_context['surt_part_options_tuples'] = \
                self._get_surt_part_options_tuples(
                    surt_part_tree, protocol, None)
            return queryset, MAY_HAVE_DUPLICATES

        # Get the surt nav option tuples.
        self.custom_context['surt_part_options_tuples'] = \
            self._get_surt_part_options_tuples(surt_part_tree, protocol, surt)

        # In serious stream-of-consciousness coding territory here....should
        # definitely break this stuff up. lol.... lol...

        # Create a surt query for both verbatim and wildcard matches.
        if self.custom_context['type'] == 'Match':
            # Match the SURT query to rule surt patterns.
            queryset = queryset.extra(
                where=('%s LIKE surt AND %s NOT LIKE neg_surt',),
                params=(surt, surt)
            )

            # Apply the capture date filter if specified.
            capture_dt = self.custom_context['capture_date']
            capture_time = self.custom_context['capture_time']
            if capture_dt is None:
                if capture_time is not None:
                    self.custom_context['search_warnings'].append(
                        'Can not match time without a date'
                    )
            else:
                if capture_time is not None:
                    # Extend capture_dt with the capture_time.
                    capture_dt = capture_dt.replace(
                        hour=capture_time.hour,
                        minute=capture_time.minute
                    )
                queryset = queryset.filter(
                    (Q(capture_date_start__isnull=True)
                     | Q(capture_date_start__lte=capture_dt))
                    & (Q(capture_date_end__isnull=True)
                       | Q(capture_date_end__gte=capture_dt))
                )
        else:
            # Match on any rule for which this surt is prefix of its surt.
            # Maybe this is too loose a match and should be behind a flag?
            surt_query = Q(surt__startswith=surt)
            # Match on any prefix part with a trailing wildcard.
            surt_query |= Q(surt='%')
            query_parts = []
            for part in surt.split(','):
                query_parts.append(part)
                surt_query |= Q(surt=','.join(query_parts) + '%')
            queryset = queryset.filter(surt_query)

        if protocol != '':
            # Match both the specified and NULL protocol.
            queryset = queryset.filter(Q(protocol__in=('', protocol.lower())))

        return queryset, MAY_HAVE_DUPLICATES

admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleChange)
