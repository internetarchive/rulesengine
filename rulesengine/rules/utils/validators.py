from dateutil.parser import parse as parse_date
import ipaddr
import jsonschema


POLICY_CHOICES = (
    ("block", "Block playback"),
    ("message", "Block playback with message"),
    ("allow", "Allow playback"),
    ("auth", "Require auth for playback"),
    ("rewrite-all", "Rewrite playback for the entire page"),
    ("rewrite-js", "Rewrite playback JavaScript"),
    ("rewrite-headers", "Rewrite playback headers"),
)

ENVIRONMENT_CHOICES = (
    ("prod", "Production"),
    ("test", "Testing/development"),
)

SCHEMA = {
    "type": "object",
    "properties": {
        "policy": {"enum": [choice[0] for choice in POLICY_CHOICES]},
        "enabled": {"type": "boolean"},
        "environment": {"enum": [choice[0] for choice in ENVIRONMENT_CHOICES]},
        "surt": {"type": "string"},
        "neg_surt": {"type": "string"},
        "protocol": {"type": "string"},
        "subdomain": {"type": "string"},
        "status_code": {"type": "integer"},
        "capture_date": {
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": [
                "start",
                "end",
            ],
        },
        "retrieve_date": {
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": [
                "start",
                "end",
            ],
        },
        "ip_range": {
            "type": "object",
            "properties": {
                "start": {"type": "string"},
                "end": {"type": "string"},
            },
            "required": [
                "start",
                "end",
            ],
        },
        "seconds_since_capture": {"type": "integer"},
        "collection": {"type": "string"},
        "partner": {"type": "string"},
        "warc_match": {"type": "string"},
        "rewrite_from": {"type": "string"},
        "rewrite_to": {"type": "string"},
        "private_comment": {"type": "string"},
        "public_comment": {"type": "string"},
    },
    "required": [
        "policy",
        "environment",
        "enabled",
        "surt",
    ],
}


def validate_rule_json(input):
    """Validate incoming JSON against a schema."""
    jsonschema.validate(input, SCHEMA)
    if "capture_date" in input:
        try:
            parse_date(input["capture_date"]["start"])
        except ValueError as e:
            raise ValueError(("capture start date", e))
        try:
            parse_date(input["capture_date"]["end"])
        except ValueError as e:
            raise ValueError(("capture end date", e))
    if "retrieve_date" in input:
        try:
            parse_date(input["retrieve_date"]["start"])
        except ValueError as e:
            raise ValueError(("retrieve start date", e))
        try:
            parse_date(input["retrieve_date"]["end"])
        except ValueError as e:
            raise ValueError(("retrieve end date", e))
    if "ip_range" in input:
        try:
            ipaddr.IPAddress(input["ip_range"]["start"])
        except ValueError as e:
            raise ValueError(("ip range start", e))
        try:
            ipaddr.IPAddress(input["ip_range"]["end"])
        except ValueError as e:
            raise ValueError(("ip range end", e))
