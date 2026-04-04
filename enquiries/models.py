"""
enquiries/models.py
Lead capture from CTA form, property pages, and agent contact.
"""
from django.db import models
from django.conf import settings


class Enquiry(models.Model):
    class EnquiryType(models.TextChoices):
        BUY          = 'buy',          'Buy Property'
        RENT         = 'rent',         'Rent Property'
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

    # CRM
    status       = models.CharField(max_length=15, choices=Status.choices, default=Status.NEW)
    notes        = models.TextField(blank=True, help_text='Internal agent/admin notes')
    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Enquiry'
        verbose_name_plural = 'Enquiries'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.name} — {self.enquiry_type} ({self.status})'
