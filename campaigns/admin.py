"""
campaigns/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Campaign, CampaignHighlight


class CampaignHighlightInline(admin.TabularInline):
    model   = CampaignHighlight
    extra   = 3
    fields  = ('order', 'icon', 'heading', 'body')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display  = ('title', 'developer_name', 'color_swatch', 'nav_style', 'footer_style', 'is_active', 'created_at')
    list_filter   = ('is_active', 'nav_style', 'footer_style')
    search_fields = ('title', 'developer_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines       = [CampaignHighlightInline]

    fieldsets = (
        ('Identity', {
            'fields': ('title', 'slug', 'developer_name', 'developer_logo', 'accent_color', 'is_active'),
        }),
        ('Header / Nav', {
            'fields': ('nav_style', 'nav_cta_text', 'nav_show_links'),
        }),
        ('Hero', {
            'fields': ('hero_heading', 'hero_sub', 'hero_bg'),
        }),
        ('Offer Banner', {
            'fields': ('offer_label', 'offer_expiry'),
            'classes': ('collapse',),
        }),
        ('About Section', {
            'fields': ('about_heading', 'about_body'),
            'classes': ('collapse',),
        }),
        ('CTA Block', {
            'fields': ('cta_heading', 'cta_sub', 'cta_button_text'),
            'classes': ('collapse',),
        }),
        ('Relations', {
            'fields': ('assigned_agent', 'properties'),
        }),
        ('Footer', {
            'fields': (
                'footer_style', 'footer_tagline', 'footer_address',
                'footer_email', 'footer_facebook', 'footer_instagram',
                'footer_youtube', 'footer_copyright',
            ),
            'classes': ('collapse',),
        }),
    )

    def color_swatch(self, obj):
        return format_html(
            '<span style="display:inline-block;width:18px;height:18px;'
            'border-radius:3px;background:{};border:1px solid #ccc;"></span>',
            obj.accent_color
        )
    color_swatch.short_description = 'Colour'
