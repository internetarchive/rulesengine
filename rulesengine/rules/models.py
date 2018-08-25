from datetime import datetime
from dateutil.parser import parse as parse_date

from django.db import models


class RuleBase(models.Model):
    """Abstract model representing the base fields for rules and changes."""

    POLICY_CHOICES = (
        ('block', 'Block playback'),
        ('message', 'Block playback with message'),
        ('allow', 'Allow playback'),
        ('auth', 'Require auth for playback'),
        ('rewrite-all', 'Rewrite playback for the entire page'),
        ('rewrite-js', 'Rewrite playback JavaScript'),
        ('rewrite-headers', 'Rewrite playback headers'),
    )

    policy = models.CharField(max_length=10, choices=POLICY_CHOICES)

    # Used for surt and surt-neg rules
    surt = models.TextField()
    # SURT Negation example: rewrite everything but a given path
    neg_surt = models.TextField(blank=True)

    # Used for daterange rules
    capture_date_start = models.DateTimeField(null=True)
    capture_date_end = models.DateTimeField(null=True)
    retrieve_date_start = models.DateTimeField(null=True)
    retrieve_date_end = models.DateTimeField(null=True)
    seconds_since_capture = models.IntegerField(null=True)

    # Used for WARC-related rules
    collection = models.TextField(blank=True)
    partner = models.TextField(blank=True)
    warc_match = models.TextField(blank=True)

    # Rewrite rules
    rewrite_from = models.TextField(blank=True)
    rewrite_to = models.TextField(blank=True)

    # Metadata
    private_comment = models.TextField(blank=True)
    public_comment = models.TextField(blank=True)
    enabled = models.BooleanField(default=True)

    class Meta:
        abstract = True

    def populate(self, values):
        """Given an object á là `summary`, populate the given fields.

        Arguments:
        values -- A Python dict containing keys named after the fields in the
            model.
        """
        self.policy = values['policy']
        self.surt = values['surt']
        self.neg_surt = values.get('neg_surt', '')
        if values.get('capture_date_start'):
            if isinstance(values['capture_date_start'], datetime):
                self.capture_date_start = values['capture_date_start']
            else:
                self.capture_date_start = parse_date(
                    values['capture_date_start'])
        if values.get('capture_date_end'):
            if isinstance(values['capture_date_end'], datetime):
                self.capture_date_end = values['capture_date_end']
            else:
                self.capture_date_end = parse_date(
                    values['capture_date_end'])
        if values.get('retrieve_date_start'):
            if isinstance(values['retrieve_date_start'], datetime):
                self.retrieve_date_start = values['retrieve_date_start']
            else:
                self.retrieve_date_start = parse_date(
                    values['retrieve_date_start'])
        if values.get('retrieve_date_end'):
            if isinstance(values['retrieve_date_end'], datetime):
                self.retrieve_date_end = values['retrieve_date_end']
            else:
                self.retrieve_date_end = parse_date(
                    values['retrieve_date_end'])
        self.seconds_since_capture = values.get('seconds_since_capture')
        self.collection = values.get('collection', '')
        self.partner = values.get('partner', '')
        self.warc_match = values.get('warc_match', '')
        self.rewrite_from = values.get('rewrite_from', '')
        self.rewrite_to = values.get('rewrite_to', '')
        self.public_comment = values.get('public_comment', '')
        self.private_comment = values.get('private_comment', '')
        self.enabled = values['enabled'] == 'true'


class Rule(RuleBase):
    """Represents a rule for exclusion, inclusion, or modification."""

    def summary(self):
        """Returns an object with publicly visible fields."""
        return {
            'id': self.id,
            'policy': self.policy,
            'surt': self.surt,
            'neg_surt': self.neg_surt,
            'capture_date_start': self.capture_date_start,
            'capture_date_end': self.capture_date_end,
            'retrieve_date_start': self.retrieve_date_start,
            'retrieve_date_end': self.retrieve_date_end,
            'seconds_since_capture': self.seconds_since_capture,
            'collection': self.collection,
            'partner': self.partner,
            'warc_match': self.warc_match,
            'rewrite_from': self.rewrite_from,
            'rewrite_to': self.rewrite_to,
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
        The policy type, the rule type, and the pertinent field
        """
        return '{} ({})'.format(
            self.get_policy_display().upper(),
            self.surt)

    def save(self, *args, **kwargs):
        """Create a RuleChange entry on save."""
        change = RuleChange(
            change_user=kwargs.get('user', ''),
            change_comment=kwargs.get('comment', ''))
        if self.pk is None:
            change.change_type = 'c'
            change.surt = self.surt
            change.policy = self.policy
        else:
            change.change_type = 'u'
            existing = Rule.objects.get(pk=self.pk)
            change.populate(existing.full_values())
        super().save(*args, **kwargs)
        change.rule = self
        change.save()

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
    )
    rule = models.ForeignKey(
        Rule,
        on_delete=models.CASCADE,
        related_name='rule_change')
    change_date = models.DateTimeField(auto_now=True)
    change_user = models.TextField(blank=True)
    change_comment = models.TextField(blank=True)
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
            'policy': self.policy,
            'surt': self.surt,
            'neg_surt': self.neg_surt,
            'capture_date_start': self.capture_date_start,
            'capture_date_end': self.capture_date_end,
            'retrieve_date_start': self.retrieve_date_start,
            'retrieve_date_end': self.retrieve_date_end,
            'seconds_since_capture': self.seconds_since_capture,
            'collection': self.collection,
            'partner': self.partner,
            'warc_match': self.warc_match,
            'rewrite_from': self.rewrite_from,
            'rewrite_to': self.rewrite_to,
            'public_comment': self.public_comment,
            'private_comment': self.private_comment,
            'enabled': self.enabled,
        }
