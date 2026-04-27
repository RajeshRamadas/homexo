"""
HOMEXO — Root URL Configuration
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from django.views.generic import TemplateView
from pages import views as pages_views
from accounts import views as accounts_views

from .sitemaps import sitemaps

# ─── Admin Customisation ──────────────────────────────────────────────────────
admin.site.site_header  = 'HOMEXO Administration'
admin.site.site_title   = 'HOMEXO Admin'
admin.site.index_title  = 'Portal Management'

urlpatterns = [
    # SEO
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('robots.txt', TemplateView.as_view(template_name='robots.txt', content_type='text/plain'), name='robots'),

    # Admin
    path('admin/', admin.site.urls),

    # Direct developers link for debugging (ensures no shadowing)
    path('developers/', pages_views.developers, name='developers_root'),

    # Advocate self-registration
    path('advocate-signup/', accounts_views.advocate_register_view, name='advocate_signup'),

    # Frontend pages
    path('',               include('pages.urls',        namespace='pages')),
    path('properties/',    include('properties.urls',   namespace='properties')),
    path('blog/',          include('blog.urls',          namespace='blog')),
    path('enquiries/',     include('enquiries.urls',     namespace='enquiries')),
    path('wishlist/',      include('wishlist.urls',      namespace='wishlist')),
    path('accounts/',      include('accounts.urls',      namespace='accounts')),
    path('social-auth/',   include('social_django.urls',  namespace='social')),
    path('legal-tracking/', include('legal_services.urls', namespace='legal_services')),

    # REST API (v1)
    path('api/v1/',        include('homexo.api_urls',   namespace='api')),

    # AI Chatbot (Urvashi RAG)
    path('api/v1/',        include('chatbot.urls',       namespace='chatbot')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL,  document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
