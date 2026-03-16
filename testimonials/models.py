"""
testimonials/models.py
"""
from django.db import models
from django.conf import settings


class Testimonial(models.Model):
    user         = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL,
                                     null=True, blank=True)
    client_name  = models.CharField(max_length=120)
    client_location = models.CharField(max_length=120, blank=True)
    avatar       = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    rating       = models.PositiveSmallIntegerField(default=5,
                                                    help_text='Rating out of 5')
    review       = models.TextField()
    property     = models.ForeignKey('properties.Property', on_delete=models.SET_NULL,
                                     null=True, blank=True)
    is_active    = models.BooleanField(default=True)
    order        = models.PositiveSmallIntegerField(default=0)
    created_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Testimonial'
        verbose_name_plural = 'Testimonials'
        ordering            = ['order', '-created_at']

    def __str__(self):
        return f'{self.client_name} — {self.rating}★'
