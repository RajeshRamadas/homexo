from django.contrib import admin
from .models import Developer

@admin.register(Developer)
class DeveloperAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "location", "established")
    prepopulated_fields = {"slug": ("name",)}
    search_fields = ("name", "location", "tags")
    list_filter = ("location",)
