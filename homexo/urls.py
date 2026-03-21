"""
HOMEXO — Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

# ─── Admin Customisation ──────────────────────────────────────────────────────
admin.site.site_header  = 'HOMEXO Administration'
admin.site.site_title   = 'HOMEXO Admin'
admin.site.index_title  = 'Portal Management'

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),

    # Frontend pages
    path('',               include('pages.urls',        namespace='pages')),
    path('properties/',    include('properties.urls',   namespace='properties')),
    path('agents/',        include('agents.urls',        namespace='agents')),
    path('blog/',          include('blog.urls',          namespace='blog')),
    path('enquiries/',     include('enquiries.urls',     namespace='enquiries')),
    path('wishlist/',      include('wishlist.urls',      namespace='wishlist')),
    path('accounts/',      include('accounts.urls',      namespace='accounts')),
    path('campaigns/',     include('campaigns.urls',      namespace='campaigns')),

    # REST API (v1)
    path('api/v1/',        include('homexo.api_urls',   namespace='api')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
