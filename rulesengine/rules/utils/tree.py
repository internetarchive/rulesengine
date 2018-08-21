from datetime import (
    datetime,
    timezone,
)

from django.db.models import Q

from rules.models import Rule


def tree(surt, neg_surt=None, collection=None, partner=None,
         warc_match=None, capture_date=None):
    """Retrieves rules for all parts of the surt up to and including the
    provided surt.

    E.g: http://(org,archive,)/somepage attempts to fetch the following rules:

    * -
    * http://(
    * http://(org,
    * http://(org,archive,
    * http://(org,archive,)
    * http://(org,archive,)/somepage

    Arguments:
    surt -- The SURT to find the tree of rules for.

    Returns:
    A QuerySet of rules that match each level of the tree.
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
    filters = (Q(surt__in=tree_surts) | Q(surt__startswith=surt)) & (
        Q(enabled=True)) & (
        Q(retrieve_date_start__isnull=False) &
        Q(retrieve_date_end__isnull=False) &
        Q(retrieve_date_start__lt=now) &
        Q(retrieve_date_end__gt=now))
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
