"""
HOMEXO — REST API URL Configuration (v1)
All API endpoints are prefixed with /api/v1/
"""

from django.urls import path, include

app_name = 'api'

urlpatterns = [
    path('properties/',  include('properties.api_urls')),
    path('blog/',        include('blog.api_urls')),
    path('enquiries/',   include('enquiries.api_urls')),
    path('accounts/',    include('accounts.api_urls')),
    path('wishlist/',    include('wishlist.api_urls')),
]
