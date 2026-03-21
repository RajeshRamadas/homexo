"""
campaigns/views.py
"""

from django.shortcuts import render, get_object_or_404
from .models import Campaign


def campaign_list(request):
    campaigns = Campaign.objects.filter(is_active=True).prefetch_related('highlights')
    return render(request, 'campaigns/list.html', {'campaigns': campaigns})


def campaign_detail(request, slug):
    campaign = get_object_or_404(Campaign, slug=slug, is_active=True)
    properties = campaign.properties.filter(status='active').prefetch_related('images')[:6]
    return render(request, 'campaigns/detail.html', {
        'campaign':   campaign,
        'properties': properties,
    })
