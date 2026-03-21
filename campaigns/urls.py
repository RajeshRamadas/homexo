"""
campaigns/urls.py
"""

from django.urls import path
from . import views

app_name = 'campaigns'

urlpatterns = [
    path('',             views.campaign_list,   name='list'),
    path('<slug:slug>/', views.campaign_detail, name='detail'),
]
