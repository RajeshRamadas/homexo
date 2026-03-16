"""
agents/admin.py
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Agent


@admin.register(Agent)
class AgentAdmin(admin.ModelAdmin):
    list_display   = ('photo_thumb', 'full_name', 'phone', 'specialization',
                      'experience_years', 'rera_number', 'is_verified', 'is_active',
                      'rating', 'listings_count')
    list_display_links = ('full_name',)
    list_filter    = ('is_verified', 'is_active')
    search_fields  = ('user__first_name', 'user__last_name', 'user__email', 'rera_number')
    list_editable  = ('is_verified', 'is_active')
    raw_id_fields  = ('user',)

    @admin.display(description='Photo')
    def photo_thumb(self, obj):
        if obj.photo:
            return format_html('<img src="{}" width="40" height="40" style="border-radius:50%;object-fit:cover;" />', obj.photo.url)
        return '—'

    @admin.display(description='Name')
    def full_name(self, obj):
        return obj.user.get_full_name()

    @admin.display(description='Listings')
    def listings_count(self, obj):
        return obj.listings_count
