"""
blog/admin.py
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Post, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ('cover_thumb', 'title', 'category', 'author', 'status',
                      'is_featured', 'views_count', 'published_at')
    list_display_links = ('title',)
    list_filter    = ('status', 'is_featured', 'category')
    search_fields  = ('title', 'body', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    list_editable  = ('status', 'is_featured')
    date_hierarchy = 'published_at'
    readonly_fields = ('views_count', 'created_at', 'updated_at')

    @admin.display(description='Cover')
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:4px;" />', obj.cover_image.url)
        return '—'
