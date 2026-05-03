"""
blog/admin.py
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Post, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'color')
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display   = ('cover_thumb', 'title', 'category_badges', 'author', 'status',
                      'is_featured', 'views_count', 'published_at', 'open_editor_btn')
    list_display_links = ('title',)
    list_filter    = ('status', 'is_featured', 'categories')
    search_fields  = ('title', 'body', 'excerpt')
    prepopulated_fields = {'slug': ('title',)}
    list_editable  = ('status', 'is_featured')
    date_hierarchy = 'published_at'
    readonly_fields = ('views_count', 'created_at', 'updated_at', 'editor_link')
    fieldsets = (
        ('Content', {'fields': ('editor_link', 'title', 'slug', 'author', 'categories', 'excerpt', 'key_takeaways', 'body', 'cover_image')}),
        ('Publishing', {'fields': ('status', 'is_featured', 'published_at')}),
        ('SEO Metadata', {'fields': ('meta_title', 'meta_description'), 'classes': ('collapse',)}),
        ('Stats', {'fields': ('views_count', 'created_at', 'updated_at'), 'classes': ('collapse',)}),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('categories')

    @admin.display(description='Categories')
    def category_badges(self, obj):
        cats = obj.categories.all()
        if not cats:
            return '—'
        return format_html(' '.join(
            '<span style="display:inline-block;padding:2px 8px;border-radius:3px;'
            'background:{};color:#fff;font-size:11px;margin:1px;">{}</span>'.format(
                c.color, c.name
            ) for c in cats
        ))

    @admin.display(description='Cover')
    def cover_thumb(self, obj):
        if obj.cover_image:
            return format_html('<img src="{}" width="60" height="40" style="object-fit:cover;border-radius:4px;" />', obj.cover_image.url)
        return '—'

    @admin.display(description='Visual Editor')
    def open_editor_btn(self, obj):
        url = reverse('blog:edit', kwargs={'slug': obj.slug})
        return format_html(
            '<a href="{}" target="_blank" style="'
            'display:inline-block;padding:4px 12px;'
            'background:#0D2B4E;color:#fff;font-size:11px;'
            'letter-spacing:1px;text-decoration:none;border-radius:3px;">'
            '&#9998; Editor</a>',
            url
        )

    @admin.display(description='')
    def editor_link(self, obj):
        if not obj.pk:
            return '—'
        url = reverse('blog:edit', kwargs={'slug': obj.slug})
        return format_html(
            '<a href="{}" target="_blank" style="'
            'display:inline-flex;align-items:center;gap:6px;'
            'padding:8px 20px;background:#0D2B4E;color:#fff;'
            'font-size:12px;letter-spacing:1.5px;text-transform:uppercase;'
            'text-decoration:none;border-radius:3px;">'
            '&#9998;&nbsp; Open Visual Editor</a>',
            url
        )

    def get_urls(self):
        from django.urls import path
        urls = super().get_urls()
        extra = [
            path('create-with-editor/', self.admin_site.admin_view(self._redirect_to_create),
                 name='blog_post_editor_create'),
        ]
        return extra + urls

    def _redirect_to_create(self, request):
        from django.shortcuts import redirect
        return redirect(reverse('blog:create'))

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['new_post_editor_url'] = reverse('blog:create')
        return super().changelist_view(request, extra_context=extra_context)
