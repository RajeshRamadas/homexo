from django.db import models

# Developer model has been consolidated into properties.models.Developer.
# This file is intentionally kept minimal; add page-specific models here if needed.

class HeroSlider(models.Model):
    developer_name = models.CharField(max_length=100, help_text="e.g. SANJEEVINI")
    developer_subtitle = models.CharField(max_length=100, blank=True, help_text="e.g. GROUP or ESTANCIA")
    rera_text = models.CharField(max_length=255, blank=True)
    
    headline = models.CharField(max_length=200, help_text="Main headline text")
    headline_highlight = models.CharField(max_length=100, blank=True, help_text="Specific word in headline to highlight")
    subheadline = models.CharField(max_length=200, blank=True)
    
    image = models.ImageField(upload_to='hero_sliders/', help_text="Background hero image.")
    explore_link = models.URLField(max_length=500, blank=True, help_text="URL for the Explore Now button")
    qr_data = models.CharField(max_length=255, blank=True, help_text="Data/URL to encode in the QR code")
    
    is_dark_background = models.BooleanField(default=True, help_text="Check this if the background is dark (uses white text)")
    is_active = models.BooleanField(default=True)
    order = models.IntegerField(default=0)

    class Meta:
        ordering = ['order', '-id']

    def __str__(self):
        return f"Hero Slide: {self.developer_name}"
