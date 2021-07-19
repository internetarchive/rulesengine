"""
TODO - Error URLs

http://rulesengine-local:8080/admin/rules/rule/?q=%3A%2F%2F(com%2Cyoutube)%2Fwatch%3Fv%3Dnz2x22z8en4%26feature%3Drelated%25&type=Match

"""

import re
from datetime import datetime
from functools import lru_cache
from itertools import chain

import urlcanon
from django.contrib import admin
from django.db import connection
from django.db.models import Q
from django.db.models.expressions import Col
from django.db.models.fields import TextField
from django.db.models.lookups import (
    Exact,
    LessThan,
    StartsWith,
)

from djangoql.admin import DjangoQLSearchMixin
from djangoql.exceptions import DjangoQLError
from djangoql.schema import (
    DjangoQLSchema,
    StrField,
)

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

class URLField(StrField):
    """Define a custom djangoql field to support searching for a SURT by URL.
    """
    model = Rule
    name = 'url'

    def get_lookup_name(self):
        return 'surt'

    def get_lookup_value(self, value):
        """Return a URL as a SURT.
        """
        # Ensure that value starts with a scheme to make surt() work as
        # expected. e.g. value = 'facebook.com' = parsed.surt()
        if value.startswith('://'):
            value = 'http{}'.format(value)
        elif not value.startswith(('http://', 'https://')):
            value = 'http://{}'.format(value)
        parsed = urlcanon.parse_url(value)

        # Add a trailing slash if necessary to get ensure that the
        # resulting SURT includes it.
        parsed.path = parsed.path or b'/'
        # Exclude the scheme and trailing comma from the SURT.
        surt = parsed.surt(with_scheme=False, trailing_comma=False)\
                     .decode('utf-8')
        return surt

    def get_lookup(self, path, operator, value):
        """Override the '=' operator to perform a actual matching operation
        (i.e. LIKE surt) between the URL and surt patterns.
        """
        if operator != '=':
            return super().get_lookup(path, operator, value)
        surt = self.get_lookup_value(value)
        # Return a query that Django can easily represent (and which doesn't
        # make sense [i.e. < surt] in any normal context), the left/right-hand
        # sides of which we'll convert into a match query in
        # RuleAdmin.get_search_results().
        return Q(surt__lt=surt)

class SURTPrefixField(StrField):
    """Define a custom djangoql field to support searching for a SURT by
    prefix.
    """
    model = Rule
    name = 'surt_prefix'

    def get_lookup_name(self):
        return 'surt'

    def get_lookup(self, path, operator, value):
        """Override the '=' operator to perform a actual matching operation
        (i.e. LIKE surt) between the URL and surt patterns.
        """
        if operator != '=':
            raise DjangoQLError(
                'Only the "=" operator is supported for surt_prefix'
            )
        return Q(surt__startswith=value)

class RuleQLSchema(DjangoQLSchema):
    def get_fields(self, model):
        fields = super(RuleQLSchema, self).get_fields(model)
        if model == Rule:
            fields += [URLField(), SURTPrefixField()]
        return fields

# Register your models here.
class RuleAdmin(DjangoQLSearchMixin, admin.ModelAdmin):
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

    djangoql_schema = RuleQLSchema

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
        self.custom_context = {}

    def get_search_results(self, request, queryset, search_term):
        queryset, not_uniq = super().get_search_results(
            request, queryset, search_term)

        # Since djangoql only affords the return of Q() objects from
        # get_lookup(), with which it appears impossible to express:
        #   "<surt-literal>" LIKE surt
        # we've chosen to express this in get_lookup() as
        # Q(surt__lt=surt) which we'll now remove from the whereclause
        # list and add in the correct form.
        #
        # Also taking this opportunity to other values from the whereclause
        # into self.custom_context for use downstream (e.g. surt-part-nav)
        #
        surt_match_strs = []
        new_children = []
        # Reset the custom query context.
        self.custom_context['surt_prefix'] = ''
        self.custom_context['protocol'] = ''
        for child in queryset.query.where.children:
            if (isinstance(child, (LessThan, StartsWith))
                and child.lhs.target.name == 'surt'
                and isinstance(child.rhs, str)
                ):
                if isinstance(child, LessThan):
                    # This is a URLField match query.
                    surt_match_strs.append(child.rhs)
                else:
                    # This is a SURTPrefixField query.
                    # Save the prefix query string to custom_context for use
                    # by the surt-part-navigator form in setting values as
                    # selected.
                    self.custom_context['surt_prefix'] = child.rhs
                    new_children.append(child)
            elif (isinstance(child, Exact)
                  and child.lhs.target.name == 'protocol'
                  and isinstance(child.rhs, str)
                ):
                # Save any protocol query to custom_context for use
                # by the surt-part-navigator form in setting values as
                # selected.
                self.custom_context['protocol'] = child.rhs
                new_children.append(child)
            else:
                new_children.append(child)
        # Replace the children.
        queryset.query.where.children = new_children
        # Add the SURT match queries.
        for surt_s in surt_match_strs:
            queryset = queryset.extra(
                where=['%s LIKE surt AND %s NOT LIKE neg_surt'],
                params=(surt_s, surt_s)
            )

        return queryset, not_uniq

    def _get_surt_part_options_tuples(self, surt_part_tree, protocol, surt):
        """Return an ordered list of (<current-surt-part>,
        <all-surt-tree-part-options>) for the current search.
        """
        surt_part_options_tuples = []
        d = surt_part_tree
        # Always include the protocol selector.
        surt_part_options_tuples.append((protocol, sorted(d.keys())))

        if protocol == '':
            # If protocol is the empty string, include all protocols dicts.
            dicts = tuple(d.values())
        else:
            # Otherwise, just includes the specified protocol dict.
            dicts = (d[protocol],)

        get_next_keys = \
            lambda dicts: sorted(set(chain(*(tuple(d.keys()) for d in dicts))))

        get_next_dicts = \
            lambda dicts, part: [d[part] for d in dicts if part in d]

        if surt:
            for part in surt.split(')', 1)[0].split(','):
                surt_part_options_tuples.append((part, get_next_keys(dicts)))
                dicts = get_next_dicts(dicts, part)
                if not dicts:
                    # If part does not exist in any surt_part_tree dict, pop
                    # the last options tuple so that it's subsequently,
                    # correctly added as a next-direct-descendant selector and
                    # do break.
                    surt_part_options_tuples.pop()
                    break

        # Add a final default-empty pair that list any available, immediate
        # descendants.
        if dicts:
            surt_part_options_tuples.append(('', [''] + get_next_keys(dicts)))

        return surt_part_options_tuples

    def changelist_view(self, request, *args, **kwargs):
        # Get the default response.
        response = super().changelist_view(request, *args, **kwargs)

        surt_part_tree = get_surt_part_tree()
        self.custom_context['surt_part_options_tuples'] = \
            self._get_surt_part_options_tuples(
                surt_part_tree,
                protocol=self.custom_context['protocol'],
                surt=self.custom_context['surt_prefix']
            )

        # Attach custom context to the cl (changelist) object in order to make
        # it available in the template (e.g. search form error) because no
        # amount of messing around with the Django-native extra_context
        # argument seems to work.
        response.context_data['cl'].custom_context = self.custom_context
        return response

admin.site.register(Rule, RuleAdmin)
admin.site.register(RuleChange)
