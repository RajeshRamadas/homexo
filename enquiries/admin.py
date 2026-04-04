"""
enquiries/admin.py
"""
from django.contrib import admin
from .models import Enquiry


@admin.register(Enquiry)
class EnquiryAdmin(admin.ModelAdmin):
    list_display  = ('name', 'email', 'phone', 'enquiry_type', 'source',
                     'budget', 'property', 'status', 'follow_up_at', 'created_at')
    list_filter   = ('status', 'enquiry_type', 'source', 'created_at')
    search_fields = ('name', 'email', 'phone', 'message', 'source')
    list_editable = ('status',)
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy  = 'created_at'
    ordering        = ('-created_at',)

    fieldsets = (
        ('Contact',  {'fields': ('name', 'email', 'phone', 'user')}),
        ('Details',  {'fields': ('enquiry_type', 'budget', 'message', 'property')}),
        ('Source',   {'fields': ('source',)}),
        ('CRM',      {'fields': ('status', 'assigned_to', 'follow_up_at', 'notes')}),
        ('Meta',     {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )
