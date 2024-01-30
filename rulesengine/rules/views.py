from dateutil.parser import parse as parse_date
import json

from django.views import View
from django.views.generic.detail import SingleObjectMixin

from .models import Rule
from .utils.json import (
    error,
    success,
)
from .utils.validators import validate_rule_json


class RulesView(View):
    """Contains RESTful views for dealing with the rules collection."""

    def get(self, request, *args, **kwargs):
        """Gets a list of all rules."""
        if request.GET.get("surt-exact") is not None:
            rules = Rule.objects.filter(surt=request.GET.get("surt-exact"))
        elif request.GET.get("surt-start") is not None:
            rules = Rule.objects.filter(surt__startswith=request.GET.get("surt-start"))
        else:
            rules = Rule.objects.all()
        return success([rule.summary() for rule in rules])

    def post(self, request, *args, **kwargs):
        """Creates a single rule in the collection."""
        try:
            new_rule = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return error("unable to marshal json", str(e))
        try:
            validate_rule_json(new_rule)
        except Exception as e:
            return error("error validating json", str(e))
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
            updates = json.loads(request.body.decode("utf-8"))
        except Exception as e:
            return error("unable to marshal json", str(e))
        try:
            validate_rule_json(updates)
        except Exception as e:
            return error("error validating json", str(e))
        rule.populate(updates)
        rule.save()
        change = rule.rule_change.order_by("-id")[0]
        return success(
            {
                "rule": rule.summary(),
                "change": change.full_change(),
            }
        )

    def delete(self, request, *args, **kwargs):
        rule = self.get_object()
        rule.delete()
        return success({})


def rules_for_surt(request, surt_string=None):
    """Fetches rules for a given surt."""
    result = [rule.summary() for rule in rules_query(surt_string)]
    return success(result)


def rules_for_request(request):
    """Returns all rules that would apply to a surt, and
       other optional parameters.

    Query string parameters:
    surt -- The SURT to look up.
    neg-surt -- A SURT negation (e.g: surt does not match) to take
        into account.
    collection -- A collection id to match against.
    partner -- A partner id to match against.
    capture-date -- The date the playback data was captured (ISO 8601)."""
    surt_qs = request.GET.get("surt")
    if surt_qs is None:
        return error("surt query string param is required", {})
    capture_date_qs = request.GET.get("capture-date")
    capture_date = None
    if capture_date_qs:
        try:
            capture_date = parse_date(capture_date_qs)
        except ValueError as e:
            return error(
                "capture-date query string param must be " "a datetime", str(e)
            )
    rules_result = rules_query(
        surt_qs,
        neg_surt=request.GET.get("neg-surt"),
        collection=request.GET.get("collection"),
        partner=request.GET.get("partner"),
        capture_date=capture_date,
    )
    return success([rule.summary() for rule in rules_result])


def rules_query(
    surt_qs,
    enabled_only=True,
    include_retrieval_dates=True,
    neg_surt=None,
    collection=None,
    partner=None,
    capture_date=None,
):
    """Retrieves rules matching surt_qs and other optional parameters.

    Arguments:
    surt_qs -- The SURT to match.
    neg_surt -- A SURT to not match.[1]
    collection -- Match against a partner's collection.
    partner -- Match against a partner.
    warc_match -- Match against a WARC filename (regex allowed).
                  (not yet implemented)
    capture_date -- The date of the requested capture.

    Returns:
    A QuerySet of matching rules
    """

    from datetime import (
        datetime,
        timezone,
    )

    from django.db.models import Q

    rules_result = Rule.objects.extra(where=["%s LIKE surt"], params=[surt_qs])
    now = datetime.now(timezone.utc)
    filters = Q()
    if enabled_only:
        filters = filters & Q(enabled=True)
    if include_retrieval_dates:
        filters = filters & (
            (Q(retrieve_date_end__isnull=True) | Q(retrieve_date_end__gt=now))
            & (Q(retrieve_date_start__isnull=True) | Q(retrieve_date_start__lt=now))
        )
    if neg_surt is not None:
        filters = filters & Q(neg_surt=neg_surt)
    if collection is not None:
        filters = filters & (Q(collection=collection) | Q(collection=""))
    if partner is not None:
        filters = filters & (Q(partner=partner) | Q(partner=""))
    if capture_date is not None:
        filters = filters & (
            (Q(capture_date_end__isnull=True) | Q(capture_date_end__gt=capture_date))
            & (
                Q(capture_date_start__isnull=True)
                | Q(capture_date_start__lt=capture_date)
            )
        )
    return rules_result.filter(filters)
