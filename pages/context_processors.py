"""
pages/context_processors.py
Injects global data available in every template:
  - nav listing types
  - wishlist count for logged-in user
  - site settings / branding
"""
from properties.models import Property


def global_context(request):
    wishlist_count = 0
    if request.user.is_authenticated:
        try:
            wishlist_count = request.user.wishlist.count()
        except Exception:
            pass

    return {
        'SITE_NAME':      'HOMEXO',
        'SITE_TAGLINE':   'Luxury Real Estate',
        'LISTING_TYPES':  Property.ListingType.choices,
        'wishlist_count': wishlist_count,
    }
