from dateutil.parser import isoparse as parse_date
import json

from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Rule
from .utils.json import (
    error,
    success,
)
from .utils.surt import Surt
from .utils.tree import tree
from .utils.validators import validate_rule_json


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

    def post(self, request, *args, **kwargs):
        """Creates a single rule in the collection."""
        try:
            new_rule = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            return error('unable to marshal json', str(e))
        try:
            validate_rule_json(new_rule)
        except Exception as e:
            return error('error validating json', str(e))
        rule = Rule()
        rule.populate(new_rule)
        rule.save()
        return success(rule.summary())


class RuleView(SingleObjectMixin, View):
    """Contains RESTful views for dealing with individual rules."""

    model = Rule

    def get(self, request, *args, **kwargs):
        """Gets a single rule."""
        rule = self.get_object()
        return success(rule.summary())

    def put(self, request, *args, **kwargs):
        """Updates a single rule and creates a changelog entry."""
        rule = self.get_object()
        try:
            updates = json.loads(request.body.decode('utf-8'))
        except Exception as e:
            return error('unable to marshal json', str(e))
        try:
            validate_rule_json(updates)
        except Exception as e:
            return error('error validating json', str(e))
        rule.populate(updates)
        rule.save()
        change = rule.rule_change.order_by('-id')[0]
        return success({
            'rule': rule.summary(),
            'change': change.full_change(),
        })

    def delete(self, request, *args, **kwargs):
        rule = self.get_object()
        rule.delete()
        return success({})


def tree_for_surt(request, surt_string=None):
    """Fetches a tree of rules for a given surt."""
    surt = Surt(surt_string)
    result = [rule.summary() for rule in tree(surt)]
    return success(result)


def rules_for_request(request):
    """Returns all rules that would apply to a warc and surt, and capture date.

    Query string parameters
    surt -- The SURT to look up.
    neg-surt -- A SURT negation (e.g: surt does not match) to take
        into account.
    collection -- A collection name to match against.
    partner -- A partner Id to match against.
    capture-date -- The date the playback data was captured (ISO 8601)."""
    surt_qs = request.GET.get('surt')
    capture_date_qs = request.GET.get('capture-date')
    if surt_qs is None or capture_date_qs is None:
        return error('surt and capture-date query string params'
                     ' are both required', {})
    try:
        capture_date = parse_date(capture_date_qs)
    except ValueError as e:
        return error(
            'capture-date query string param must be '
            'ISO 8601 format', str(e))
    surt = Surt(surt_qs)
    tree_result = tree(
        surt,
        neg_surt=request.GET.get('neg-surt'),
        collection=request.GET.get('collection'),
        partner=request.GET.get('partner'),
        capture_date=capture_date)
    return success([rule.summary() for rule in tree_result])
