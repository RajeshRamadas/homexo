"""
chatbot/models.py
──────────────────
Three models:
  • PropertyEmbedding  — vector(384) for each active Property
  • ChatSession        — groups messages per browser/user session
  • ChatMessage        — individual user/assistant turns
  • UserProfile        — per-session budget & location preferences
"""

from django.db import models
from django.conf import settings


class PropertyEmbedding(models.Model):
    """
    Stores a 384-dim sentence-transformer embedding for each Property.
    Populated by: python manage.py index_properties
    """
    property    = models.OneToOneField(
        'properties.Property',
        on_delete=models.CASCADE,
        related_name='embedding',
    )
    source_text = models.TextField(blank=True, help_text='Text that was embedded')
    # Stored as text initially; converted to vector(384) by migration 0002
    embedding   = models.TextField(null=True, blank=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Property Embedding'
        verbose_name_plural = 'Property Embeddings'

    def __str__(self):
        return f'Embedding — {self.property.title}'


class ChatSession(models.Model):
    """Groups chat messages belonging to one browser session."""
    session_key = models.CharField(max_length=128, db_index=True, unique=True)
    user        = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True, blank=True,
        on_delete=models.SET_NULL,
        related_name='chat_sessions',
    )
    created_at  = models.DateTimeField(auto_now_add=True)
    updated_at  = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Chat Session'
        verbose_name_plural = 'Chat Sessions'
        ordering            = ['-updated_at']

    def __str__(self):
        return f'Session {self.session_key[:12]}'


class ChatMessage(models.Model):
    """One user or assistant turn inside a ChatSession."""
    ROLE_CHOICES = [('user', 'User'), ('assistant', 'Assistant')]

    session    = models.ForeignKey(
        ChatSession, on_delete=models.CASCADE, related_name='messages'
    )
    role       = models.CharField(max_length=10, choices=ROLE_CHOICES)
    content    = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name        = 'Chat Message'
        verbose_name_plural = 'Chat Messages'
        ordering            = ['created_at']
        indexes             = [models.Index(fields=['session', 'created_at'])]

    def __str__(self):
        return f'[{self.role}] {self.content[:60]}'


class UserProfile(models.Model):
    """Per-session preference store (budget, locations, property type)."""
    session_key         = models.CharField(max_length=128, unique=True, db_index=True)
    budget_min          = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    budget_max          = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    property_type       = models.CharField(max_length=64, blank=True)
    updated_at          = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f'Profile — {self.session_key[:12]}'
