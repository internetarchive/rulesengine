from datetime import (
    datetime,
    timezone,
)

from django.db.models import Q

from rules.models import Rule


def tree(surt, enabled_only=True, include_retrieval_dates=True,
         neg_surt=None, collection=None, partner=None,
         warc_match=None, capture_date=None):
    """Retrieves rules for all parts of the surt up to and including the
    provided surt.[0]

    Arguments:
    surt -- The SURT to find the tree of rules for.
    neg_surt -- A SURT to not match.[1]
    collection -- Match against a partner's collection.
    partner -- Match against a partner.
    warc_match -- Match against a WARC filename (regex allowed).
    capture_date -- The date of the requested capture.

    Returns:
    A QuerySet of rules that match each level of the tree.

    [0] E.g: http://(org,archive,)/some/page attempts to fetch the following
    rules:

    * -
    * http://(
    * http://(org,
    * http://(org,archive,
    * http://(org,archive,)
    * http://(org,archive,)/some
    * http://(org,archive,)/some/page
    [1] Not currently used, but may be in the future.
    """
    surt_parts = surt.parts
    tree_surts = []
    while surt_parts != []:
        part = ''.join(surt_parts)
        if part[-1] == ')':
            part = part[0:-1]
        tree_surts.append(part)
        surt_parts.pop()
    now = datetime.now(timezone.utc)
    # This doesn't do what we want WRT dates and startswith
    filters = Q(surt__in=tree_surts)
    if enabled_only:
        filters = filters & Q(enabled=True)
    if include_retrieval_dates:
        filters = filters & ((
            Q(retrieve_date_end__isnull=True) |
            Q(retrieve_date_start__isnull=True)
            ) | (
            Q(retrieve_date_start__lt=now) &
            Q(retrieve_date_end__gt=now)))
    if neg_surt is not None:
        filters = filters & Q(neg_surt=neg_surt)
    if collection is not None:
        filters = filters & Q(collection=collection)
    if partner is not None:
        filters = filters & Q(parter=partner)
    if warc_match is not None:
        filters = filters & Q(warc_match__regex=warc_match)
    if capture_date is not None:
        filters = filters & (
            Q(capture_date_start__isnull=False) &
            Q(capture_date_end__isnull=False) &
            Q(capture_date_start__lt=capture_date) &
            Q(capture_date_end__gt=capture_date))
    return Rule.objects.filter(filters)
