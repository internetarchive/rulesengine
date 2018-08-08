from rules.models import Rule


def tree_for_surt(surt):
    """Retrieves rules for all parts of the surt up to and including the
    provided surt.

    E.g: http://(org,archive,)/somepage attempts to fetch the following rules:

    * http://(
    * http://(org,
    * http://(org,archive,)
    * http://(org,archive,)/somepage
    """
    surt_parts = surt.parts
    tree_surts = []
    while surt_parts != []:
        part = ''.join(surt_parts)
        if part[-1] == ')':
            part = part[0:-1]
        tree_surts.append(part)
        surt_parts.pop()
    tree_rules = []
    for tree_part in tree_surts:
        for rule in Rule.objects.filter(surt=tree_part):
            tree_rules.append(rule)
    return tree_rules
