"""
enquiries/models.py
Lead capture from CTA form, property pages, and agent contact.
"""
from django.db import models
from django.conf import settings


class Enquiry(models.Model):
    class EnquiryType(models.TextChoices):
        BUY          = 'buy',          'Buy Property'
        SELL         = 'sell',         'Sell / List Property'
        HOME_LOAN    = 'home_loan',    'Home Loan'
        LEGAL        = 'legal',        'Property Legal'
        SECURITY     = 'security',     'Security Services'
        HOME_SERVICE = 'home_service', 'Home Services'
        GENERAL      = 'general',      'General'

    class Status(models.TextChoices):
        NEW        = 'new',        'New'
        CONTACTED  = 'contacted',  'Contacted'
        QUALIFIED  = 'qualified',  'Qualified'
        CLOSED     = 'closed',     'Closed'
        LOST       = 'lost',       'Lost'

    class Priority(models.TextChoices):
        CRITICAL = 'critical', 'Critical'
        HIGH     = 'high',     'High'
        MEDIUM   = 'medium',   'Medium'
        LOW      = 'low',      'Low'

    # Who submitted
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='enquiries')
    # What they're enquiring about
    property     = models.ForeignKey('properties.Property', on_delete=models.SET_NULL,
                                     null=True, blank=True, related_name='enquiries')

    # Contact details (in case user is not logged in)
    name         = models.CharField(max_length=120)
    email        = models.EmailField(blank=True)
    phone        = models.CharField(max_length=20)

    # Enquiry details
    enquiry_type = models.CharField(max_length=20, choices=EnquiryType.choices, default=EnquiryType.GENERAL)
    budget       = models.CharField(max_length=50, blank=True)
    message      = models.TextField(blank=True)

    # Source tracking — which page / section the form was submitted from
    source       = models.CharField(max_length=120, blank=True,
                                    help_text='Page or section the form was submitted from')

    # CRM
    status       = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    priority     = models.CharField(max_length=10, choices=Priority.choices, default=Priority.MEDIUM)
    assigned_to  = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='assigned_enquiries',
        help_text='Team member responsible for follow-up',
    )
    follow_up_at      = models.DateTimeField(null=True, blank=True,
                                             help_text='Scheduled follow-up date/time')
    first_response_at = models.DateTimeField(null=True, blank=True,
                                             help_text='When first agent action was taken on this ticket')
    notes        = models.TextField(blank=True, help_text='Internal agent/admin notes')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Enquiry'
        verbose_name_plural = 'Enquiries'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.enquiry_type} ({self.status})'


class EnquiryActivity(models.Model):
    """Append-only history log for a single enquiry ticket."""

    class Kind(models.TextChoices):
        COMMENT       = 'comment',       'Comment'
        STATUS_CHANGE = 'status_change', 'Status Change'
        FOLLOWUP_SET  = 'followup_set',  'Follow-up Scheduled'
        ASSIGNED      = 'assigned',      'Assigned'
        SYSTEM        = 'system',        'System'

    enquiry   = models.ForeignKey(Enquiry, on_delete=models.CASCADE, related_name='activities')
    actor     = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
        null=True, blank=True, related_name='enquiry_activities',
    )
    kind      = models.CharField(max_length=20, choices=Kind.choices, default=Kind.COMMENT)
    body      = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        actor = self.actor.get_full_name() if self.actor else 'System'
        return f'[{self.kind}] {actor}: {self.body[:60]}'
