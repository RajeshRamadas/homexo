"""
homexo/sitemaps.py
XML Sitemaps for all public pages — Properties, Blog, Static pages, Developers.
"""

from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from properties.models import Property
from blog.models import Post


class PropertySitemap(Sitemap):
    changefreq = 'weekly'
    priority = 0.8

    def items(self):
        return Property.objects.filter(status='active')

    def lastmod(self, obj):
        return obj.updated_at


class BlogSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.7

    def items(self):
        return Post.objects.filter(status='published')

    def lastmod(self, obj):
        return obj.updated_at


class StaticViewSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return [
            'pages:home',
            'pages:about',
            'pages:contact',
            'pages:faq',
            'pages:developers',
            'pages:emi_calculator',
            'pages:security',
            'pages:home_service',
            'pages:legal',
            'pages:legal_homeloan',
            'pages:home_loan',
            'pages:area_guides',
            'pages:market_reports',
            'properties:list',
            'blog:list',
        ]

    def location(self, item):
        return reverse(item)


# Developer profile slugs (same as in pages/views.py)
_DEVELOPER_SLUGS = [
    'prestige-group', 'sobha-limited', 'godrej-properties',
    'brigade-group', 'mahindra-lifespaces', 'dlf-limited',
    'puravankara', 'oberoi-realty', 'k-raheja-corp', 'sunteck-realty',
]


class DeveloperSitemap(Sitemap):
    changefreq = 'monthly'
    priority = 0.6

    def items(self):
        return _DEVELOPER_SLUGS

    def location(self, slug):
        return reverse('pages:developer_profile', kwargs={'slug': slug})


# Registry used by urls.py
sitemaps = {
    'properties': PropertySitemap,
    'blog': BlogSitemap,
    'static': StaticViewSitemap,
    'developers': DeveloperSitemap,
}
