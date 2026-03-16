"""
wishlist/models.py
User saved/favourited properties.
"""
from django.db import models
from django.conf import settings


class WishlistItem(models.Model):
    user       = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                   related_name='wishlist')
    property   = models.ForeignKey('properties.Property', on_delete=models.CASCADE,
                                   related_name='wishlisted_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together     = ('user', 'property')
        verbose_name        = 'Wishlist Item'
        verbose_name_plural = 'Wishlist Items'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.user.email} → {self.property.title}'
