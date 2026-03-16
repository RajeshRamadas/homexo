from django.contrib import admin
from .models import WishlistItem


@admin.register(WishlistItem)
class WishlistItemAdmin(admin.ModelAdmin):
    list_display  = ('user', 'property', 'created_at')
    list_filter   = ('created_at',)
    search_fields = ('user__email', 'property__title')
    raw_id_fields = ('user', 'property')
