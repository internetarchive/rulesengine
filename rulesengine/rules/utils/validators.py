class RuleValidationException(Exception):
    pass


def validate_rule_json(rule_json):
    # TODO use jsonschema
    REQUIRED_FIELDS = [
        'policy',
        'surt',
        'capture_start',
        'capture_end',
        'retrieval_start',
        'retrieval_end',
        'seconds_since_capture',
        'who',
        'enabled',
    ]
    # OPTIONAL_FIELDS = [
    #     'private_comment',
    #     'public_comment',
    # ]

    missing_fields = []
    for field in REQUIRED_FIELDS:
        if field not in rule_json:
            missing_fields.append(field)
    if len(missing_fields) != 0:
        raise RuleValidationException(
            "Required fields missing: {}".format(', '.join(missing_fields)))
