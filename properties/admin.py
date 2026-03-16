"""
properties/admin.py
Rich admin panel for Property management.
"""

from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyImage, PropertyFeature, PropertyTag


class PropertyImageInline(admin.TabularInline):
    model      = PropertyImage
    extra      = 3
    fields     = ('image', 'image_thumb', 'caption', 'is_primary', 'order')
    readonly_fields = ('image_thumb',)

    @admin.display(description='Preview')
    def image_thumb(self, obj):
        if obj.image:
            return format_html('<img src="{}" height="60" style="border-radius:4px;object-fit:cover;" />', obj.image.url)
        return '—'


class PropertyFeatureInline(admin.TabularInline):
    model = PropertyFeature
    extra = 4
    fields = ('name', 'icon')


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display   = ('primary_thumb', 'title', 'listing_type', 'property_type',
                      'display_price', 'locality', 'city', 'bedrooms', 'bathrooms',
                      'is_featured', 'is_signature', 'status', 'views_count', 'created_at')
    list_display_links = ('title',)
    list_filter    = ('status', 'listing_type', 'property_type', 'city',
                      'is_featured', 'is_signature', 'is_new')
    search_fields  = ('title', 'locality', 'city', 'address', 'owner__email')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'display_price')
    list_editable  = ('is_featured', 'is_signature', 'status')
    date_hierarchy = 'created_at'
    ordering       = ('-created_at',)
    inlines        = [PropertyImageInline, PropertyFeatureInline]
    filter_horizontal = ('tags',)

    fieldsets = (
        ('Basic Info', {
            'fields': ('title', 'slug', 'listing_type', 'property_type', 'description',
                       'owner', 'agent', 'status')
        }),
        ('Pricing', {
            'fields': ('price', 'display_price', 'price_label', 'price_on_req')
        }),
        ('Location', {
            'fields': ('address', 'locality', 'city', 'state', 'pincode',
                       'latitude', 'longitude')
        }),
        ('Dimensions', {
            'fields': ('bhk', 'bedrooms', 'bathrooms', 'area_sqft', 'carpet_area',
                       'floor_no', 'total_floors')
        }),
        ('Details', {
            'fields': ('furnishing', 'facing', 'age_years', 'parking_slots', 'possession_date')
        }),
        ('Flags & Tags', {
            'fields': ('is_featured', 'is_signature', 'is_new', 'is_exclusive', 'tags')
        }),
        ('Meta', {
            'fields': ('views_count', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

    @admin.display(description='Image')
    def primary_thumb(self, obj):
        img = obj.primary_image
        if img and img.image:
            return format_html('<img src="{}" width="60" height="45" style="object-fit:cover;border-radius:4px;" />', img.image.url)
        return format_html('<div style="width:60px;height:45px;background:#0D2B4E;border-radius:4px;"></div>')

    @admin.display(description='Price')
    def display_price(self, obj):
        return obj.display_price


@admin.register(PropertyTag)
class PropertyTagAdmin(admin.ModelAdmin):
    list_display        = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
