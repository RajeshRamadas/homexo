"""
testimonials/admin.py
"""
from django.contrib import admin
from .models import Testimonial


@admin.register(Testimonial)
class TestimonialAdmin(admin.ModelAdmin):
    list_display  = ('client_name', 'client_location', 'rating', 'is_active', 'order', 'created_at')
    list_filter   = ('rating', 'is_active')
    list_editable = ('is_active', 'order')
    search_fields = ('client_name', 'review')
