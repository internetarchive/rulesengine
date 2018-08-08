from datetime import datetime
import json

from django.shortcuts import render
from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import (
    Rule,
    RuleChange,
)
from .utils.json import (
    error,
    success,
)
from .utils.surt import Surt
from .utils.tree import tree_for_surt
from .utils.validators import (
    RuleValidationException,
    validate_rule_json,
)


class RulesView(View):
    """Contains RESTful views for dealing with the rules collection."""

    def get(self, request, *args, **kwargs):
        """Gets a list of all rules."""
        if request.GET.get('surt-exact') is not None:
            rules = Rule.objects.filter(surt=request.GET.get('surt-exact'))
        elif request.GET.get('surt-start') is not None:
            rules = Rule.objects.filter(
                surt__startswith=request.GET.get('surt-start'))
        else:
            rules = Rule.objects.all()
        return success([rule.summary() for rule in rules])

    def put(self, request, *args, **kwargs):
        """Creates a single rule in the collection."""
        try:
            new_rule = json.loads(request.body)
        except Exception as e:
            return error('unable to marshal json', str(e))
        try:
            validate_rule_json(new_rule)
        except RuleValidationException as e:
            return error('error validating json', str(e))
        rule = Rule()
        rule.populate(new_rule)
        rule.save()
        return success(rule.summary())


class RuleView(SingleObjectMixin, View):
    """Contains RESTful views for dealing with individual rules."""

    model = Rule

    def get(self, request):
        """Gets a single rule."""
        rule = self.get_object()
        return success(rule.summary())

    def post(self, request, *args, **kwargs):
        """Updates a single rule and creates a changelog entry."""
        rule = self.get_object()
        try:
            updates = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            return error('unable to marshal json', str(e))
        try:
            validate_rule_json(updates)
        except RuleValidationException as e:
            return error('error validating json', str(e))

        # TODO this can take place in the save method on Rule, which would also
        # cover creation and deletion.
        change = RuleChange(
            rule=rule,
            change_user=updates['user'],
            change_comment=updates['comment'])
        change.populate(rule.full_values())
        if rule.enabled and not updates['enabled']:
            change.change_type = 'd'
        else:
            change.change_type = 'u'
        change.save()
        rule.populate(updates)
        rule.save()
        return success({
            'rule': rule.summary(),
            'change': change.summary(),
        })

    def delete(self, request, *args, **kwargs):
        rule = self.get_object()
        rule.delete()
        return success({})


def tree(request, surt_string):
    """Fetches a tree of rules for a given surt."""
    surt = Surt(surt_string)
    tree = [rule.summary() for rule in tree_for_surt(surt)]
    return success(tree)


def rules_for_request(request):
    """Returns all rules that would apply to a warc, surt, and capture date.

    capture-date should be in the format yyyymmddhhmm"""
    surt = request.GET.get('surt')
    warc = request.GET.get('warc')
    capture_date = int(request.GET.get('capture-date')) # XXX try/except
    if surt is None or warc is None or capture_date is None:
        return error('surt, warc, and capture-date query string params'
                     ' are all required', {})
    surt = Surt(surt)
    tree = tree_for_surt(surt)
    warc_parts = warc.split('-') # XXX validate warc name
    warc_date = int(warc_parts[4][0:-5]) # Parse an int out of the date minus ms
    applicable_rules = []
    for rule in tree:
        start = int(rule.capture_start.strftime('%Y%m%d%H%M'))
        end = int(rule.capture_end.strftime('%Y%m%d%H%M'))
        if ((warc_date > start and warc_date < end) and
            (capture_date > start and capture_date < end)):
            applicable_rules.append(rule)
    # Here is where we would make a surface-level decision on the action to
    # be taken (block, auth, allow, rewrite, etc). A point of optimization would
    # be to use django to only select the rules matching the date range, but for
    # now, we select the whole tree. Also, date comparisons would probably be
    # faster than coercing to strings, then to ints, but I was running short
    # on time.
    return success([rule.summary() for rule in applicable_rules])

# Stub out how rules apply
# Indexes
# Performance vs current
#   Plus how to improve
# Lifecycle
