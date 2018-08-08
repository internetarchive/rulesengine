from django.db import models


class RuleBase(models.Model):
    """Abstract model representing the base fields for rules and changes."""

    POLICY_CHOICES = (
        ('b', 'block'),
        ('a', 'allow'),
        ('r', 'robots'),
    )

    RULE_TYPES = (
        ('surt', 'SURT'),
        ('surt-neg', 'SURT negation'),
        ('regex', 'regular expression'),
        ('daterange', 'date range'),
        ('warcname', 'WARC name (or regex)'),
    )

    policy = models.CharField(max_length=1, choices=POLICY_CHOICES)
    rule_type = models.CharField(max_length=10, choices=RULE_TYPES)
    # We would also include a payload field here for any rewrite data and such
    surt = models.TextField()
    capture_start = models.DateTimeField()
    capture_end = models.DateTimeField()
    retrieval_start = models.DateTimeField()
    retrieval_end = models.DateTimeField()
    seconds_since_capture = models.IntegerField()
    who = models.CharField(max_length=50)
    private_comment = models.TextField(blank=True)
    public_comment = models.TextField(blank=True)
    enabled = models.BooleanField()

    class Meta:
        abstract = True

    def populate(self, values):
        """Given an object á là `summary`, populate the given fields.

        Arguments:
        values -- A Python dict containing keys named after the fields in the
            model.
        """
        self.surt = values['surt']
        self.capture_start = values['capture_start']
        self.capture_end = values['capture_end']
        self.retrieval_start = values['retrieval_start']
        self.retrieval_end = values['retrieval_end']
        self.seconds_since_capture = values['seconds_since_capture']
        self.who = values['who']
        self.enabled = values['enabled']
        # Optional arguments
        if 'public_comment' in values:
            self.public_comment = values['public_comment']
        if 'private_comment' in values:
            self.private_comment = values['private_comment']


class Rule(RuleBase):
    """Represents a rule for exclusion, inclusion, or modification."""

    def summary(self):
        """Returns an object with publicly visible fields."""
        return {
            'id': self.id,
            'policy': self.get_policy_display(),
            'surt': self.surt,
            'capture_start': self.capture_start,
            'capture_end': self.capture_end,
            'retrieval_start': self.retrieval_start,
            'retrieval_end': self.retrieval_end,
            'seconds_since_capture': self.seconds_since_capture,
            'who': self.who,
            'public_comment': self.public_comment,
            'enabled': self.enabled,
        }

    def full_values(self):
        """Get the summary of the rule plus the private comment.

        Returns:
        The full values of the rule.
        """
        summary = self.summary()
        summary['private_comment'] = self.private_comment
        return summary

    def __str__(self):
        """Get a string representation of the rule for the Django admin.

        Returns:
        The policy type and the SURT
        """
        return '{} {}'.format(self.get_policy_display().upper(), self.surt)

    class Meta:
        indexes = [
            models.Index(fields=['surt'])
            # Any additional indices would be created here.
        ]
        ordering = ['surt']


class RuleChange(RuleBase):
    """Represents a change to a rule in the database."""

    TYPE_CHOICES = (
        ('c', 'created'),
        ('u', 'updated'),
        ('d', 'deleted'),
    )
    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        related_name='rule_change')
    change_date = models.DateTimeField(auto_now=True)
    change_user = models.TextField()
    change_comment = models.TextField()
    change_type = models.CharField(max_length=1, choices=TYPE_CHOICES)

    def summary(self):
        """Get a brief summary of the rule change.

        Returns:
        An object with all non-rule fields.
        """
        return {
            'id': self.id,
            'rule_id': self.rule.id,
            'date': self.change_date,
            'user': self.change_user,
            'comment': self.change_comment,
            'type': self.get_change_type_display(),
        }

    def full_change(self):
        """Get the full rule change.

        Returns:
        An object with the old rule fields and the change metadata.
        """
        return {
            'id': self.id,
            'rule_id': self.rule.id,
            'date': self.change_date,
            'user': self.change_user,
            'comment': self.change_comment,
            'type': self.get_change_type_display(),
            'policy': self.get_policy_display(),
            'surt': self.surt,
            'capture_start': self.capture_start,
            'capture_end': self.capture_end,
            'retrieval_start': self.retrieval_start,
            'retrieval_end': self.retrieval_end,
            'seconds_since_capture': self.seconds_since_capture,
            'who': self.who,
            'public_comment': self.public_comment,
            'private_comment': self.private_comment,
            'enabled': self.enabled,
        }
