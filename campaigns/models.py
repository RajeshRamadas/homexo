"""
campaigns/models.py
Developer campaign landing pages — fully customisable nav & footer per record.
"""

from django.db import models
from django.utils.text import slugify
from agents.models import Agent
from properties.models import Property


class Campaign(models.Model):

    class NavStyle(models.TextChoices):
        COBRANDED = 'cobranded', 'Co-branded (HOMEXO + Developer)'
        BRANDED   = 'branded',   'Developer Branded (dark nav)'
        MINIMAL   = 'minimal',   'Minimal (logo + CTA only)'
        HOMEXO    = 'homexo',    'HOMEXO Default'

    class FooterStyle(models.TextChoices):
        BRANDED = 'branded', 'Developer Branded Footer'
        HOMEXO  = 'homexo',  'Full HOMEXO Footer'
        MINIMAL = 'minimal', 'Minimal (copyright bar only)'

    # ── Identity ──────────────────────────────────────────────────────────
    title           = models.CharField(max_length=200)
    slug            = models.SlugField(max_length=200, unique=True, blank=True)
    developer_name  = models.CharField(max_length=200)
    developer_logo  = models.ImageField(upload_to='campaigns/logos/', blank=True, null=True)
    accent_color    = models.CharField(
        max_length=7, default='#4A90C4',
        help_text='Hex colour, e.g. #4A90C4'
    )
    is_active       = models.BooleanField(default=True)
    created_at      = models.DateTimeField(auto_now_add=True)
    updated_at      = models.DateTimeField(auto_now=True)

    # ── Header / Nav ──────────────────────────────────────────────────────
    nav_style       = models.CharField(
        max_length=20, choices=NavStyle.choices, default=NavStyle.COBRANDED
    )
    nav_cta_text    = models.CharField(max_length=80, default='Book a Site Visit')
    nav_show_links  = models.BooleanField(
        default=True, help_text='Show nav links (About / Properties / Contact)'
    )

    # ── Hero ──────────────────────────────────────────────────────────────
    hero_heading    = models.CharField(
        max_length=200,
        help_text='Use | to split into two lines, e.g. "Discover|Prestige"'
    )
    hero_sub        = models.CharField(max_length=300, blank=True)
    hero_bg         = models.ImageField(
        upload_to='campaigns/heroes/', blank=True, null=True,
        help_text='Optional hero background image (falls back to gradient)'
    )

    # ── Offer banner ─────────────────────────────────────────────────────
    offer_label     = models.CharField(max_length=120, blank=True)
    offer_expiry    = models.DateTimeField(
        blank=True, null=True,
        help_text='If set, a countdown timer appears on the detail page'
    )

    # ── About section ─────────────────────────────────────────────────────
    about_heading   = models.CharField(max_length=200, blank=True)
    about_body      = models.TextField(blank=True)

    # ── CTA block ─────────────────────────────────────────────────────────
    cta_heading     = models.CharField(max_length=200, blank=True)
    cta_sub         = models.CharField(max_length=300, blank=True)
    cta_button_text = models.CharField(max_length=80, blank=True, default='Book a Free Consultation')

    # ── Relations ─────────────────────────────────────────────────────────
    assigned_agent  = models.ForeignKey(
        Agent, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='campaigns'
    )
    properties      = models.ManyToManyField(
        Property, blank=True, related_name='campaigns'
    )

    # ── Footer ────────────────────────────────────────────────────────────
    footer_style     = models.CharField(
        max_length=20, choices=FooterStyle.choices, default=FooterStyle.BRANDED
    )
    footer_tagline   = models.CharField(max_length=300, blank=True)
    footer_address   = models.TextField(blank=True)
    footer_email     = models.EmailField(blank=True)
    footer_facebook  = models.URLField(blank=True)
    footer_instagram = models.URLField(blank=True)
    footer_youtube   = models.URLField(blank=True)
    footer_copyright = models.CharField(
        max_length=250, blank=True,
        help_text='Leave blank to auto-generate "© 2026 <developer_name>. Powered by HOMEXO."'
    )

    class Meta:
        verbose_name        = 'Campaign'
        verbose_name_plural = 'Campaigns'
        ordering            = ['-created_at']

    def __str__(self):
        return f'{self.developer_name} — {self.title}'

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    @property
    def hero_heading_parts(self):
        parts = self.hero_heading.split('|', 1)
        return (parts[0].strip(), parts[1].strip() if len(parts) > 1 else '')

    @property
    def effective_copyright(self):
        if self.footer_copyright:
            return self.footer_copyright
        from django.utils import timezone
        year = timezone.now().year
        return f'\u00a9 {year} {self.developer_name}. Powered by HOMEXO.'


class CampaignHighlight(models.Model):
    campaign = models.ForeignKey(
        Campaign, on_delete=models.CASCADE, related_name='highlights'
    )
    icon     = models.CharField(
        max_length=10, default='\u2713',
        help_text='Unicode character or emoji used as the bullet icon'
    )
    heading  = models.CharField(max_length=120)
    body     = models.CharField(max_length=300, blank=True)
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.campaign} / {self.heading}'
