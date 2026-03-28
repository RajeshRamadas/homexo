"""
properties/models.py
Core models: Property, PropertyImage, PropertyFeature, PropertyTag.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class PropertyTag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    class Meta:
        verbose_name        = 'Tag'
        verbose_name_plural = 'Tags'
        ordering            = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Property(models.Model):
    """
    Central property listing model.
    Covers all transaction types shown in the HOMEXO portal.
    """

    class ListingType(models.TextChoices):
        BUY        = 'buy',        'Buy'
        RENT       = 'rent',       'Rent'
        NEW_PROJ   = 'new_project','New Project'
        COMMERCIAL = 'commercial', 'Commercial'

    class PropertyType(models.TextChoices):
        APARTMENT  = 'apartment',  'Apartment'
        VILLA      = 'villa',      'Villa'
        PENTHOUSE  = 'penthouse',  'Penthouse'
        PLOT       = 'plot',       'Plot / Land'
        OFFICE     = 'office',     'Office Space'
        SHOP       = 'shop',       'Shop / Retail'
        WAREHOUSE  = 'warehouse',  'Warehouse'

    class BHK(models.TextChoices):
        STUDIO  = 'studio', 'Studio'
        ONE     = '1bhk',   '1 BHK'
        TWO     = '2bhk',   '2 BHK'
        THREE   = '3bhk',   '3 BHK'
        FOUR    = '4bhk',   '4 BHK'
        FIVE    = '5bhk',   '5 BHK'
        SIX_P   = '6+bhk',  '6+ BHK'

    class Status(models.TextChoices):
        ACTIVE    = 'active',    'Active'
        SOLD      = 'sold',      'Sold'
        RENTED    = 'rented',    'Rented'
        PENDING   = 'pending',   'Pending Approval'
        DRAFT     = 'draft',     'Draft'
        INACTIVE  = 'inactive',  'Inactive'

    class FurnishingStatus(models.TextChoices):
        FURNISHED    = 'furnished',     'Fully Furnished'
        SEMI         = 'semi',          'Semi Furnished'
        UNFURNISHED  = 'unfurnished',   'Unfurnished'

    class OwnershipType(models.TextChoices):
        FREEHOLD   = 'freehold',   'Freehold'
        LEASEHOLD  = 'leasehold',  'Leasehold'
        COOP       = 'coop',       'Co-operative Society'
        POA        = 'poa',        'Power of Attorney'

    # ── Ownership & Classification ────────────────────────────────────────────
    owner          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='owned_properties')
    agent          = models.ForeignKey('agents.Agent', on_delete=models.SET_NULL,
                                       null=True, blank=True, related_name='listings')
    listing_type   = models.CharField(max_length=20, choices=ListingType.choices, default=ListingType.BUY)
    property_type  = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.APARTMENT)

    # ── Core Details ──────────────────────────────────────────────────────────
    title          = models.CharField(max_length=200)
    slug           = models.SlugField(max_length=220, unique=True, blank=True)
    description    = models.TextField(blank=True)
    bhk            = models.CharField(max_length=10, choices=BHK.choices, blank=True)

    # ── Price ─────────────────────────────────────────────────────────────────
    price          = models.DecimalField(max_digits=14, decimal_places=2)
    price_label    = models.CharField(max_length=50, blank=True,
                                      help_text='e.g. "/ Onwards", "/ Month"')
    price_on_req   = models.BooleanField(default=False, verbose_name='Price on Request')

    # ── Location ──────────────────────────────────────────────────────────────
    address        = models.TextField()
    locality       = models.CharField(max_length=100)
    city           = models.CharField(max_length=100, default='Bengaluru')
    state          = models.CharField(max_length=100, default='Karnataka')
    pincode        = models.CharField(max_length=10, blank=True)
    latitude       = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)
    longitude      = models.DecimalField(max_digits=10, decimal_places=7, null=True, blank=True)

    # ── Dimensions ────────────────────────────────────────────────────────────
    bedrooms       = models.PositiveSmallIntegerField(default=0)
    bathrooms      = models.PositiveSmallIntegerField(default=0)
    area_sqft      = models.PositiveIntegerField(null=True, blank=True, verbose_name='Area (sq.ft)')
    carpet_area    = models.PositiveIntegerField(null=True, blank=True, verbose_name='Carpet Area (sq.ft)')
    floor_no       = models.PositiveSmallIntegerField(null=True, blank=True)
    total_floors   = models.PositiveSmallIntegerField(null=True, blank=True)

    # ── Additional Info ───────────────────────────────────────────────────────
    furnishing      = models.CharField(max_length=15, choices=FurnishingStatus.choices, blank=True)
    facing          = models.CharField(max_length=50, blank=True, help_text='e.g. East, North-East')
    age_years       = models.PositiveSmallIntegerField(null=True, blank=True,
                                                       verbose_name='Property Age (years)')
    parking_slots   = models.PositiveSmallIntegerField(default=0)
    possession_date = models.DateField(null=True, blank=True)
    ownership_type  = models.CharField(max_length=15, choices=OwnershipType.choices, blank=True,
                                       verbose_name='Ownership Type')
    rera_approved   = models.BooleanField(default=False, verbose_name='RERA Approved')
    rera_number     = models.CharField(max_length=100, blank=True, verbose_name='RERA Registration No.')

    # ── Flags ─────────────────────────────────────────────────────────────────
    is_featured    = models.BooleanField(default=False, db_index=True)
    is_signature   = models.BooleanField(default=False, help_text='Ultra-premium / Signature collection')
    is_new         = models.BooleanField(default=True)
    is_exclusive   = models.BooleanField(default=False)

    # ── Status & Meta ─────────────────────────────────────────────────────────
    status         = models.CharField(max_length=15, choices=Status.choices, default=Status.DRAFT)
    tags           = models.ManyToManyField(PropertyTag, blank=True)
    views_count    = models.PositiveIntegerField(default=0, editable=False)
    created_at     = models.DateTimeField(auto_now_add=True)
    updated_at     = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name        = 'Property'
        verbose_name_plural = 'Properties'
        ordering            = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['listing_type', 'status']),
            models.Index(fields=['city', 'locality']),
            models.Index(fields=['is_featured', 'is_signature']),
        ]

    def __str__(self):
        return f'{self.title} — {self.locality}, {self.city}'

    def get_absolute_url(self):
        return reverse('properties:detail', kwargs={'slug': self.slug})

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            n = 1
            while Property.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f'{base_slug}-{n}'
                n += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def display_price(self):
        if self.price_on_req:
            return 'Price on Request'
        p = self.price
        if not p:
            return '—'
        if p >= 1_00_00_000:
            return f'₹{p / 1_00_00_000:.2f} Cr'
        elif p >= 1_00_000:
            return f'₹{p / 1_00_000:.2f} L'
        return f'₹{p:,.0f}'

    def increment_views(self):
        Property.objects.filter(pk=self.pk).update(views_count=models.F('views_count') + 1)


class PropertyImage(models.Model):
    property   = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image      = models.ImageField(upload_to='properties/images/')
    caption    = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order      = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Property Image'
        verbose_name_plural = 'Property Images'
        ordering            = ['order', 'id']

    def __str__(self):
        return f'Image for {self.property.title}'

    def save(self, *args, **kwargs):
        # Ensure only one primary image per property
        if self.is_primary:
            PropertyImage.objects.filter(
                property=self.property, is_primary=True
            ).exclude(pk=self.pk).update(is_primary=False)
        super().save(*args, **kwargs)


class PropertyFloorPlan(models.Model):
    """Multiple floor plan / layout images for a property."""
    property      = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='floor_plans')
    image         = models.ImageField(upload_to='properties/floor_plans/')
    caption       = models.CharField(max_length=200, blank=True)
    bhk_type      = models.CharField(
        max_length=100, blank=True,
        help_text='Config tab label, e.g. "2 BHK Apartment". Plans sharing the same bhk_type are grouped into one tab.'
    )
    size_sqft     = models.PositiveIntegerField(
        null=True, blank=True,
        help_text='Size variant in sq.ft, shown as a sub-tab, e.g. 977 or 1040.'
    )
    price_display = models.CharField(
        max_length=100, blank=True,
        help_text='Price label for this variant, e.g. "₹ 92.95 L" or "₹ 1.05 Cr".'
    )
    room_data     = models.JSONField(
        null=True, blank=True,
        help_text='Room dimensions as JSON: [{"title": "Bedroom 1", "val": "11\'0 × 11\'2"}, ...]'
    )
    image_3d      = models.ImageField(
        upload_to='properties/floor_plans/', null=True, blank=True,
        help_text='Optional 3D render of the same layout. When present, a 2D/3D toggle will appear on the viewer.'
    )
    order         = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Floor Plan'
        verbose_name_plural = 'Floor Plans'
        ordering            = ['order', 'id']

    def __str__(self):
        return f'Floor Plan for {self.property.title}'


class PropertyFeature(models.Model):
    """Amenities & features: Swimming Pool, Gym, Clubhouse, etc."""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='features')
    name     = models.CharField(max_length=100)
    icon     = models.CharField(max_length=100, blank=True, help_text='CSS icon class or SVG name')

    class Meta:
        verbose_name        = 'Feature'
        verbose_name_plural = 'Features'

    def __str__(self):
        return f'{self.name} — {self.property.title}'
