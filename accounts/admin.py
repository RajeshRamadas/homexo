"""
accounts/admin.py
Custom admin for User model.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, Notification
from .forms import AdminUserCreationForm, AdminUserChangeForm


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    form         = AdminUserChangeForm
    add_form     = AdminUserCreationForm
    list_display  = ('avatar_thumb', 'email', 'get_full_name', 'role', 'phone',
                     'is_verified', 'is_active', 'date_joined')
    list_display_links = ('email', 'get_full_name')
    list_filter   = ('role', 'is_active', 'is_verified', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name', 'phone')
    ordering      = ('-date_joined',)
    readonly_fields = ('date_joined', 'last_login')

    fieldsets = (
        ('Credentials',   {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'avatar')}),
        ('Role & Status', {'fields': ('role', 'is_active', 'is_verified', 'is_staff', 'is_superuser')}),
        ('Timestamps',    {'fields': ('date_joined', 'last_login')}),
        ('Permissions',   {'fields': ('groups', 'user_permissions'), 'classes': ('collapse',)}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields':  ('email', 'first_name', 'last_name', 'role', 'password1', 'password2'),
        }),
    )

    @admin.display(description='Avatar')
    def avatar_thumb(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" width="36" height="36" style="border-radius:50%;object-fit:cover;" />',
                obj.avatar.url
            )
        return format_html(
            '<div style="width:36px;height:36px;border-radius:50%;background:#0D2B4E;'
            'display:flex;align-items:center;justify-content:center;color:white;font-size:14px;">'
            '{}</div>', obj.first_name[:1].upper() if obj.first_name else '?'
        )

    @admin.display(description='Name')
    def get_full_name(self, obj):
        return obj.get_full_name()


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display   = ('user', 'kind', 'title', 'is_read', 'created_at')
    list_filter    = ('kind', 'is_read')
    search_fields  = ('user__email', 'title', 'body')
    readonly_fields = ('user', 'kind', 'title', 'body', 'link', 'created_at')
    list_editable  = ('is_read',)
    date_hierarchy = 'created_at'
    ordering       = ('-created_at',)
