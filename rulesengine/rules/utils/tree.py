from django.db.models import Q

from rules.models import Rule


def tree_for_surt(surt):
    """Retrieves rules for all parts of the surt up to and including the
    provided surt.

    E.g: http://(org,archive,)/somepage attempts to fetch the following rules:

    * -
    * http://(
    * http://(org,
    * http://(org,archive, # XXX TODO
    * http://(org,archive,)
    * http://(org,archive,)/somepage

    Note that this currently doesn't differentiate on rule-type. That is, it
    doesn't check any date ranges, SURT negations, or WARC files.

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
    return Rule.objects.filter(
        Q(surt__in=tree_surts) | Q(surt__startswith=surt))


# SURT always Used
# SURT negation will also \have a positive match SURT (e.g org,archive and not org,archive,api)
