from dateutil.parser import parse as parse_date

from django.db import models

from rules.utils.validators import (
    ENVIRONMENT_CHOICES,
    POLICY_CHOICES,
    validate_rule_json,
)


class RuleBase(models.Model):
    """Abstract model representing the base fields for rules and changes."""

    policy = models.CharField(
        help_text="""What action the Wayback Machine should take on encountering this rule""",  # noqa: E501
        max_length=15,
        choices=POLICY_CHOICES,
    )

    # Used for surt and surt-neg rules
    surt = models.TextField(
        verbose_name="SURT",
        help_text="""The SURT (or partial SURT) to which this rule applies. This may be an incomplete SURT which will be matched for a more specific URL.""",
    )  # noqa: E501
    # SURT Negation example: rewrite everything but a given path
    neg_surt = models.TextField(
        verbose_name="SURT negation",
        help_text="""A SURT to use as an exception (i.e: if you want to use the rewrite_from/rewrite_to fields on a broad-scope SURT, -except- a subset, that subset would be represented here)""",  # noqa: E501
        blank=True,
    )

    # Used for protocol-specific rules
    protocol = models.TextField(
        help_text="""The protocol to apply this rule to.""", blank=True  # noqa: E501???
    )

    # Used for subdomain-specific rules, for matching subdomains like www that get canonicalized away in surt form
    subdomain = models.TextField(
        help_text="""The canonicalized-away subdomain, like www, to apply this rule to.""",  # noqa: E501???
        blank=True,
    )

    # Used for daterange rules
    capture_date_start = models.DateTimeField(
        help_text="""The earliest date of capture to start applying this rule.""",  # noqa: E501
        null=True,
        blank=True,
    )
    capture_date_end = models.DateTimeField(
        help_text="""The latest date of capture to apply this rule.""",
        null=True,
        blank=True,
    )
    retrieve_date_start = models.DateTimeField(
        help_text="""The earliest date of retrieval to start applying this rule.""",  # noqa: E501
        null=True,
        blank=True,
    )
    retrieve_date_end = models.DateTimeField(
        help_text="""The latest date of retrieval to apply this rule.""",
        null=True,
        blank=True,
    )
    seconds_since_capture = models.IntegerField(
        help_text="""Number of seconds after capture to apply this rule.""",
        null=True,
        blank=True,
    )

    # Used for IP range rules
    ip_range_start = models.GenericIPAddressField(
        help_text="""The start of the IP address range to apply this rule to.""",  # noqa: E501
        null=True,
        blank=True,
    )
    ip_range_end = models.GenericIPAddressField(
        help_text="""The end of the IP address range to apply this rule to.""",  # noqa: E501
        null=True,
        blank=True,
    )

    # Used for WARC-related rules
    collection = models.TextField(
        help_text="""The collection this rule applies to.""", blank=True
    )
    partner = models.TextField(
        help_text="""The partner this rule applies to.""", blank=True
    )
    warc_match = models.TextField(
        help_text="""A regular expression for matching against a WARC name to decide whether or not this rule applies (matching must be done on the client side.)""",  # noqa: E501
        blank=True,
    )

    # Rewrite rules
    rewrite_from = models.TextField(
        help_text="""Text to match on the page that needs to be rewritten.""",
        blank=True,
    )
    rewrite_to = models.TextField(
        help_text="""Resulting text for rewrite matches.""", blank=True
    )

    # Metadata
    private_comment = models.TextField(
        help_text="""Explanatory comment visible only to rules engine admins.""",  # noqa: E501
        blank=True,
    )
    public_comment = models.TextField(
        help_text="""Publicly visible explanatory comment.""", blank=True
    )
    environment = models.TextField(
        help_text="""What environment the rule should apply to. Environments limit who can see the effects of a rule (e.g: QA environment means playback QA engineers can see the effects but the public can't).""",  # noqa: E501
        choices=ENVIRONMENT_CHOICES,
        default="prod",
    )
    enabled = models.BooleanField(
        help_text="""Whether or not the rule is enabled and returned for use.""",  # noqa: E501
        default=True,
    )

    class Meta:
        abstract = True

    def populate(self, values):
        """Given an object á là `summary`, populate the given fields.

        Arguments:
        values -- A Python dict containing keys named after the fields in the
            model.
        """
        validate_rule_json(values)
        self.policy = values["policy"]
        self.enabled = values["enabled"]
        self.environment = values["environment"]
        self.surt = values["surt"]
        self.neg_surt = values.get("neg_surt", "")
        self.protocol = values.get("protocol", "")
        self.subdomain = values.get("subdomain", "")
        if "capture_date" in values:
            self.capture_date_start = parse_date(values["capture_date"]["start"])
            self.capture_date_end = parse_date(values["capture_date"]["end"])
        if "retrieve_date" in values:
            self.retrieve_date_start = parse_date(values["retrieve_date"]["start"])
            self.retrieve_date_end = parse_date(values["retrieve_date"]["end"])
        if "ip_range" in values:
            self.ip_range_start = values["ip_range"]["start"]
            self.ip_range_end = values["ip_range"]["end"]
        self.seconds_since_capture = values.get("seconds_since_capture")
        self.collection = values.get("collection", "")
        self.partner = values.get("partner", "")
        self.warc_match = values.get("warc_match", "")
        self.rewrite_from = values.get("rewrite_from", "")
        self.rewrite_to = values.get("rewrite_to", "")
        self.public_comment = values.get("public_comment", "")
        self.private_comment = values.get("private_comment", "")

    def summary(self, include_private=False):
        """Returns an object with publicly visible fields."""
        values = {
            "id": self.id,
            "policy": self.policy,
            "environment": self.environment,
            "surt": self.surt,
            "enabled": self.enabled,
        }
        if self.neg_surt:
            values["neg_surt"] = self.neg_surt
        if self.protocol:
            values["protocol"] = self.protocol
        if self.subdomain:
            values["subdomain"] = self.subdomain
        if self.seconds_since_capture:
            values["seconds_since_capture"] = self.seconds_since_capture
        if self.collection:
            values["collection"] = self.collection
        if self.partner:
            values["partner"] = self.partner
        if self.warc_match:
            values["warc_match"] = self.warc_match
        if self.rewrite_from:
            values["rewrite_from"] = self.rewrite_from
        if self.rewrite_to:
            values["rewrite_to"] = self.rewrite_to
        if self.public_comment:
            values["public_comment"] = self.public_comment
        if include_private and self.private_comment:
            values["private_comment"] = self.private_comment
        if self.capture_date_start or self.capture_date_end:
            values["capture_date"] = {
                "start": (
                    self.capture_date_start.isoformat()
                    if self.capture_date_start
                    else None
                ),
                "end": (
                    self.capture_date_end.isoformat() if self.capture_date_end else None
                ),
            }
        if self.retrieve_date_start or self.retrieve_date_end:
            values["retrieve_date"] = {
                "start": (
                    self.retrieve_date_start.isoformat()
                    if self.retrieve_date_start
                    else None
                ),
                "end": (
                    self.retrieve_date_end.isoformat()
                    if self.retrieve_date_end
                    else None
                ),
            }
        if self.ip_range_start and self.ip_range_end:
            values["ip_range"] = {
                "start": self.ip_range_start,
                "end": self.ip_range_end,
            }
        return values


class Rule(RuleBase):
    """Represents a rule for exclusion, inclusion, or modification."""

    def full_values(self):
        """Get the summary of the rule plus the private comment.

        Returns:
        The full values of the rule.
        """
        return self.summary(include_private=True)

    def __str__(self):
        """Get a string representation of the rule for the Django admin.

        Returns:
        The policy type, the rule type, and the pertinent field
        """
        return "{} ({})".format(self.get_policy_display().upper(), self.surt)

    def save(self, *args, **kwargs):
        """Create a RuleChange entry on save."""
        change = RuleChange(
            change_user=kwargs.get("user", ""), change_comment=kwargs.get("comment", "")
        )
        if self.pk is None:
            change.change_type = "c"
            change.surt = self.surt
            change.policy = self.policy
        else:
            change.change_type = "u"
            existing = Rule.objects.get(pk=self.pk)
            change.populate(existing.full_values())
        super().save(*args, **kwargs)
        change.rule = self
        change.save()

    class Meta:
        indexes = [
            models.Index(fields=["surt"])
            # Any additional indices would be created here.
        ]
        ordering = ["surt"]


class RuleChange(RuleBase):
    """Represents a change to a rule in the database."""

    TYPE_CHOICES = (
        ("c", "created"),
        ("u", "updated"),
    )
    rule = models.ForeignKey(Rule, on_delete=models.CASCADE, related_name="rule_change")
    change_date = models.DateTimeField(auto_now=True)
    change_user = models.TextField(
        help_text="""The name of the individual making this change.""", blank=True
    )
    change_comment = models.TextField(
        help_text="""A brief explanation of the change.""", blank=True
    )
    change_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def change_summary(self):
        """Get a brief summary of the rule change.

        Returns:
        An object with all non-rule fields.
        """
        return {
            "id": self.id,
            "rule_id": self.rule.id,
            "date": self.change_date,
            "user": self.change_user,
            "comment": self.change_comment,
            "type": self.get_change_type_display(),
        }

    def full_change(self, include_private=False):
        """Get the full rule change.

        Returns:
        An object with the old rule fields and the change metadata.
        """
        values = self.change_summary()
        values["rule"] = self.summary(include_private=include_private)
        values["rule"]["id"] = self.rule.id
        return values
