"""
agents/models.py
Agent profile model, linked to User.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse


class Agent(models.Model):
    user             = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                            related_name='agent_profile')
    photo            = models.ImageField(upload_to='agents/', blank=True, null=True)
    bio              = models.TextField(blank=True)
    phone            = models.CharField(max_length=20, blank=True)
    whatsapp         = models.CharField(max_length=20, blank=True)
    specialization   = models.CharField(max_length=200, blank=True,
                                        help_text='e.g. Luxury Villas, Commercial, Plots')
    languages        = models.CharField(max_length=200, blank=True,
                                        help_text='e.g. English, Kannada, Hindi')
    experience_years = models.PositiveSmallIntegerField(default=0)
    rera_number      = models.CharField(max_length=50, blank=True, verbose_name='RERA Number')
    is_verified      = models.BooleanField(default=False)
    is_active        = models.BooleanField(default=True)
    rating           = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    total_reviews    = models.PositiveIntegerField(default=0)
    created_at       = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Agent'
        verbose_name_plural = 'Agents'
        ordering            = ['-is_verified', '-rating']

    def __str__(self):
        return f'Agent: {self.user.get_full_name()}'

    def get_absolute_url(self):
        return reverse('agents:detail', kwargs={'pk': self.pk})

    @property
    def listings_count(self):
        return self.listings.filter(status='active').count()

    @property
    def full_name(self):
        return self.user.get_full_name()

    @property
    def email(self):
        return self.user.email
