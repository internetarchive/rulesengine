
import re

import urlcanon
from django.contrib import admin
from django.db.models import Q

from .models import (
    Rule,
    RuleChange
)

SEARCH_TERM_REGEX = re.compile(r'^(?:(?P<protocol>\w+)://)?(?P<rest>.*)$')

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
            # If the search_term specifies no protocol, prepend one for the same
            # of generating the SURT. Exclude the scheme and trailing comma from
            # the SURT.
            parsed = urlcanon.parse_url(
                search_term if protocol else 'http://{}'.format(search_term)
            )
            # Add a trailing slash if necessary to get ensure that the resulting
            # SURT includes it.
            parsed.path = parsed.path or b'/'
            surt = parsed.surt(
                with_scheme=False,
                trailing_comma=False
            ).decode('utf-8')

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
