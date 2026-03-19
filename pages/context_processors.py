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
    wishlist_ids = []
    if request.user.is_authenticated:
        try:
            qs = request.user.wishlist.values_list('property_id', flat=True)
            wishlist_ids = list(qs)
            wishlist_count = len(wishlist_ids)
        except Exception:
            pass

    return {
        'SITE_NAME':      'HOMEXO',
        'SITE_TAGLINE':   'Luxury Real Estate',
        'LISTING_TYPES':  Property.ListingType.choices,
        'wishlist_count': wishlist_count,
        'wishlist_ids':   wishlist_ids,
    }
