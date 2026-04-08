from django.contrib import admin
from .models import HeroSlider

@admin.register(HeroSlider)
class HeroSliderAdmin(admin.ModelAdmin):
    list_display = ('developer_name', 'headline', 'is_active', 'order')
    list_editable = ('is_active', 'order')
    search_fields = ('developer_name', 'headline')
