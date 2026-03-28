from django.db import models
from django.utils.text import slugify

class Developer(models.Model):
    name = models.CharField(max_length=128, unique=True)
    slug = models.SlugField(max_length=128, unique=True, blank=True)
    initials = models.CharField(max_length=8, blank=True)
    tagline = models.CharField(max_length=256, blank=True)
    tags = models.CharField(max_length=256, blank=True, help_text="Comma-separated tags")
    location = models.CharField(max_length=128, blank=True)
    established = models.CharField(max_length=64, blank=True)
    workforce = models.CharField(max_length=64, blank=True)
    presence = models.CharField(max_length=256, blank=True)
    listed_on = models.CharField(max_length=128, blank=True)
    contact = models.CharField(max_length=64, blank=True)
    about_p1 = models.TextField(blank=True)
    about_p2 = models.TextField(blank=True)
    about_p3 = models.TextField(blank=True)
    # Add more fields as needed

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
