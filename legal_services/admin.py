from django.contrib import admin
from .models import LegalOrder, OrderStep, VerdictCheck

class OrderStepInline(admin.TabularInline):
    model = OrderStep
    extra = 0

class VerdictCheckInline(admin.TabularInline):
    model = VerdictCheck
    extra = 0

@admin.register(LegalOrder)
class LegalOrderAdmin(admin.ModelAdmin):
    list_display = ('order_id', 'property_name', 'user', 'package', 'verdict', 'created_at')
    list_filter = ('verdict', 'package')
    search_fields = ('order_id', 'property_name', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('order_id', 'uuid', 'created_at', 'updated_at')
    inlines = [OrderStepInline, VerdictCheckInline]
