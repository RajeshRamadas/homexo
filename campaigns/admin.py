"""
campaigns/admin.py
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import (
    Campaign, CampaignHighlight, CampaignFloorPlan,
    CampaignAmenity, CampaignGalleryImage,
)


class CampaignHighlightInline(admin.TabularInline):
    model   = CampaignHighlight
    extra   = 3
    fields  = ('order', 'icon', 'heading', 'body')


class CampaignFloorPlanInline(admin.TabularInline):
    model   = CampaignFloorPlan
    extra   = 2
    fields  = ('order', 'config', 'sba_range', 'price_range', 'image', 'plan_pdf')


class CampaignAmenityInline(admin.TabularInline):
    model   = CampaignAmenity
    extra   = 3
    fields  = ('order', 'icon', 'name', 'description')


class CampaignGalleryImageInline(admin.TabularInline):
    model   = CampaignGalleryImage
    extra   = 3
    fields  = ('order', 'image', 'caption')


@admin.register(Campaign)
class CampaignAdmin(admin.ModelAdmin):
    list_display  = ('title', 'developer_name', 'color_swatch', 'nav_style', 'footer_style', 'is_active', 'created_at')
    list_filter   = ('is_active', 'nav_style', 'footer_style')
    search_fields = ('title', 'developer_name')
    prepopulated_fields = {'slug': ('title',)}
    inlines       = [
        CampaignHighlightInline,
        CampaignFloorPlanInline,
        CampaignAmenityInline,
        CampaignGalleryImageInline,
    ]

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
        ('Key Stats (Hero Strip)', {
            'fields': ('stat_land_parcel', 'stat_floors', 'stat_configs', 'stat_possession', 'stat_price_start'),
            'classes': ('collapse',),
        }),
        ('Offer Banner', {
            'fields': ('offer_label', 'offer_expiry'),
            'classes': ('collapse',),
        }),
        ('About Section', {
            'fields': ('about_heading', 'about_body', 'about_image'),
            'classes': ('collapse',),
        }),
        ('Master Plan', {
            'fields': ('masterplan_heading', 'masterplan_body', 'masterplan_image'),
            'classes': ('collapse',),
        }),
        ('Location & Connectivity', {
            'fields': ('location_heading', 'location_body', 'location_map_image', 'location_map_embed'),
            'classes': ('collapse',),
        }),
        ('CTA Block', {
            'fields': ('cta_heading', 'cta_sub', 'cta_button_text'),
            'classes': ('collapse',),
        }),
        ('Disclaimer', {
            'fields': ('disclaimer',),
            'classes': ('collapse',),
        }),
        ('Relations', {
            'fields': ('assigned_agent', 'properties'),
        }),
        ('Footer', {
            'fields': (
                'footer_style', 'footer_tagline', 'footer_address',
                'footer_email', 'footer_phone', 'footer_facebook',
                'footer_instagram', 'footer_youtube', 'footer_copyright',
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
