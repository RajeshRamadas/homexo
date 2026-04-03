"""
enquiries/admin.py
"""
from django.contrib import admin
from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'enquiry_type', 'budget',
                     'property', 'status', 'created_at')
    list_filter   = ('status', 'enquiry_type', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy  = 'created_at'
    ordering        = ('-created_at',)

    fieldsets = (
        ('Contact',  {'fields': ('name', 'email', 'phone', 'user')}),
        ('Details',  {'fields': ('enquiry_type', 'budget', 'message', 'property')}),
        ('CRM',      {'fields': ('status', 'notes')}),
        ('Meta',     {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
