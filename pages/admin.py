from django.contrib import admin
from .models import HeroSlider

@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('internal_name', 'developer_name', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('internal_name', 'developer_name', 'headline')
