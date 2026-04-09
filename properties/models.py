"""
properties/models.py
Core models: Property, PropertyImage, PropertyFeature, PropertyTag.
"""

from django.db import models
from django.conf import settings
from django.urls import reverse
from django.utils.text import slugify


class Developer(models.Model):
    """
    Real estate developer / builder profile.
    """
    name             = models.CharField(max_length=200)
    slug             = models.SlugField(max_length=220, unique=True, blank=True)
    logo             = models.ImageField(upload_to='developers/logos/', blank=True, null=True)
    description      = models.TextField(blank=True)
    tagline          = models.CharField(max_length=300, blank=True)
    established_year = models.PositiveSmallIntegerField(null=True, blank=True)
    website          = models.URLField(blank=True)
    location         = models.CharField(max_length=200, blank=True, help_text='e.g. Bengaluru, Pan India')
    tags             = models.CharField(max_length=255, blank=True, help_text='Comma-separated tags (e.g. Premium, Affordable, Commercial, Luxury, Township, Plotted)')
    is_featured      = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Developer'
        verbose_name_plural = 'Developers'
        ordering            = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    @property
    def initials(self):
        parts = self.name.split(' ')
        if len(parts) > 1:
            return f"{parts[0][0]}{parts[1][0]}".upper()
        return self.name[:2].upper()

    @property
    def name_split(self):
        parts = self.name.rsplit(' ', 1)
        if len(parts) > 1:
            return (parts[0], parts[1])
        return (self.name, '')

    @property
    def name_first(self):
        return self.name_split[0]

    @property
    def name_last(self):
        return self.name_split[1]


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
        APARTMENT         = 'apartment',         'Apartment'
        INDEPENDENT_HOUSE = 'independent_house', 'Independent House/Villa'
        GATED_VILLA       = 'gated_villa',       'Gated Community Villa'
        STANDALONE        = 'standalone',        'Standalone Building'
        VILLA             = 'villa',             'Villa'
        PENTHOUSE         = 'penthouse',         'Penthouse'
        PLOT              = 'plot',              'Plot / Land'
        OFFICE            = 'office',            'Office Space'
        SHOP              = 'shop',              'Shop / Retail'
        WAREHOUSE         = 'warehouse',         'Warehouse'

    class BHK(models.TextChoices):
        STUDIO  = 'studio', 'Studio'
        ONE_RK  = '1rk',   '1 RK'
        ONE     = '1bhk',   '1 BHK'
        TWO     = '2bhk',   '2 BHK'
        THREE   = '3bhk',   '3 BHK'
        FOUR    = '4bhk',   '4 BHK'
        FIVE    = '5bhk',   '5 BHK'
        SIX_P   = '6+bhk',  '6+ BHK'

    class Status(models.TextChoices):
        ACTIVE     = 'active',     'Active'
        SOLD       = 'sold',       'Sold'
        RENTED     = 'rented',     'Rented'
        PENDING    = 'pending',    'Pending Approval'
        DRAFT      = 'draft',      'Draft'
        INACTIVE   = 'inactive',   'Inactive'
        REJECTED   = 'rejected',   'Rejected'
        NEEDS_FIX  = 'needs_fix',  'Needs Fix'

    class FurnishingStatus(models.TextChoices):
        FURNISHED    = 'furnished',     'Fully Furnished'
        SEMI         = 'semi',          'Semi Furnished'
        UNFURNISHED  = 'unfurnished',   'Unfurnished'

    class ConstructionStatus(models.TextChoices):
        READY            = 'ready',            'Ready to Move'
        UNDER_CONST      = 'under_construction','Under Construction'
        NEW_LAUNCH       = 'new_launch',       'New Launch'

    class OwnershipType(models.TextChoices):
        FREEHOLD   = 'freehold',   'Freehold'
        LEASEHOLD  = 'leasehold',  'Leasehold'
        COOP       = 'coop',       'Co-operative Society'
        POA        = 'poa',        'Power of Attorney'

    class TenantPreference(models.TextChoices):
        ANY       = 'any',      'Anyone'
        FAMILY    = 'family',   'Family Only'
        BACHELORS = 'bachelors','Bachelors Only'
        COMPANY   = 'company',  'Company Lease'

    # ── Ownership & Classification ────────────────────────────────────────────
    owner          = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
                                       related_name='owned_properties')
    listing_type   = models.CharField(max_length=20, choices=ListingType.choices, default=ListingType.BUY)
    property_type  = models.CharField(max_length=20, choices=PropertyType.choices, default=PropertyType.APARTMENT)

    # ── Core Details ──────────────────────────────────────────────────────────
    title          = models.CharField(max_length=200)
    slug           = models.SlugField(max_length=220, unique=True, blank=True)
    developer      = models.ForeignKey(Developer, on_delete=models.SET_NULL, null=True, blank=True,
                                       related_name='properties', verbose_name='Developer / Builder')
    description    = models.TextField(blank=True)
    bhk            = models.CharField(max_length=10, choices=BHK.choices, blank=True)

    # ── Price ─────────────────────────────────────────────────────────────────
    price          = models.DecimalField(max_digits=14, decimal_places=2)
    price_label    = models.CharField(max_length=50, blank=True,
                                      help_text='e.g. "/ Onwards", "/ Month"')
    price_on_req   = models.BooleanField(default=False, verbose_name='Price on Request')
    
    # ── Rent / Commercial Specific ────────────────────────────────────────────
    security_deposit   = models.DecimalField(max_digits=14, decimal_places=2, null=True, blank=True)
    maintenance_charge = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True, help_text="Monthly maintenance")
    tenant_preference  = models.CharField(max_length=15, choices=TenantPreference.choices, blank=True)
    available_from     = models.DateField(null=True, blank=True)
    lock_in_period     = models.PositiveSmallIntegerField(null=True, blank=True, help_text="Lock-in period in years")
    power_backup       = models.BooleanField(default=False)

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
    furnishing           = models.CharField(max_length=15, choices=FurnishingStatus.choices, blank=True)
    construction_status  = models.CharField(max_length=20, choices=ConstructionStatus.choices,
                                            blank=True, verbose_name='Construction Status')
    facing               = models.CharField(max_length=50, blank=True, help_text='e.g. East, North-East')
    age_years            = models.PositiveSmallIntegerField(null=True, blank=True,
                                                            verbose_name='Property Age (years)')
    parking_slots        = models.PositiveSmallIntegerField(default=0)
    two_wheeler_parking  = models.BooleanField(default=False, verbose_name='2-Wheeler Parking')
    four_wheeler_parking = models.BooleanField(default=False, verbose_name='4-Wheeler Parking')
    possession_date      = models.DateField(null=True, blank=True)
    ownership_type       = models.CharField(max_length=15, choices=OwnershipType.choices, blank=True,
                                            verbose_name='Ownership Type')
    rera_approved      = models.BooleanField(default=False, verbose_name='RERA Approved')
    rera_number        = models.CharField(max_length=100, blank=True, verbose_name='RERA Registration No.')
    title_verified     = models.BooleanField(default=False, verbose_name='Title Verified')
    is_negotiable      = models.BooleanField(default=False, verbose_name='Price Negotiable')

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

    # ── Rejection / Review tracking ───────────────────────────────────────────
    rejection_reason   = models.TextField(blank=True, help_text='Reason shown to the listing owner on rejection.')
    fix_notes          = models.TextField(blank=True, help_text='Notes sent back to owner when requesting a fix.')
    rejected_at        = models.DateTimeField(null=True, blank=True)
    auto_delete_at     = models.DateTimeField(null=True, blank=True, help_text='Rejected listings are auto-deleted after 30 days.')
    rejected_by        = models.ForeignKey(
        settings.AUTH_USER_MODEL, null=True, blank=True,
        on_delete=models.SET_NULL, related_name='rejected_properties',
    )

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
    def price_per_sqft(self):
        """Auto-computed price per sq.ft based on super built-up area."""
        if self.price and self.area_sqft and self.area_sqft > 0:
            return int(self.price / self.area_sqft)
        return None

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

    @property
    def emi_display(self):
        """EMI for 20-year loan at 7.28% p.a. (monthly reducing). Only for buy/new_project/commercial."""
        if self.price_on_req or not self.price:
            return None
        if self.listing_type == self.ListingType.RENT:
            return None
        p = float(self.price)
        r = 7.28 / 100 / 12          # monthly rate
        n = 240                       # 20 years × 12
        emi = p * r * (1 + r) ** n / ((1 + r) ** n - 1)
        if emi >= 1_00_00_000:
            return f'₹{emi / 1_00_00_000:.2f} Cr'
        elif emi >= 1_00_000:
            return f'₹{emi / 1_00_000:.2f} L'
        elif emi >= 1_000:
            return f'₹{emi / 1_000:.2f} K'
        return f'₹{emi:,.0f}'

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
    property   = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='features')
    name       = models.CharField(max_length=100)
    icon       = models.CharField(max_length=100, blank=True, help_text='CSS icon class or SVG markup')
    icon_image = models.ImageField(upload_to='features/', blank=True, help_text='Upload an icon image (PNG/SVG recommended, ~64×64px)')

    class Meta:
        verbose_name        = 'Feature'
        verbose_name_plural = 'Features'

    def __str__(self):
        return f'{self.name} — {self.property.title}'


class ConnectivityItem(models.Model):
    """Nearby landmarks / connectivity points: schools, hospitals, metro, etc."""

    class Category(models.TextChoices):
        TRANSIT    = 'transit',    'Transit'
        EDUCATION  = 'education',  'Education'
        HEALTHCARE = 'healthcare', 'Healthcare'
        SHOPPING   = 'shopping',   'Shopping'
        LIFESTYLE  = 'lifestyle',  'Lifestyle'
        OTHER      = 'other',      'Other'

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='connectivity')
    category = models.CharField(max_length=20, choices=Category.choices, default=Category.OTHER)
    name     = models.CharField(max_length=200, help_text='e.g. Whitefield Metro Station')
    distance = models.CharField(max_length=50, help_text='e.g. 2.5 km, 10 min drive')
    order    = models.PositiveSmallIntegerField(default=0)

    class Meta:
        verbose_name        = 'Connectivity Item'
        verbose_name_plural = 'Connectivity Items'
        ordering            = ['category', 'order', 'id']

    def __str__(self):
        return f'{self.name} ({self.distance}) — {self.property.title}'


class PropertyReport(models.Model):
    """User-submitted report for incorrect / misleading property information."""

    class Reason(models.TextChoices):
        WRONG_PRICE     = 'wrong_price',     'Wrong Price'
        WRONG_LOCATION  = 'wrong_location',  'Wrong Location'
        FAKE_LISTING    = 'fake_listing',     'Fake / Duplicate Listing'
        WRONG_DETAILS   = 'wrong_details',   'Incorrect Details'
        ALREADY_SOLD    = 'already_sold',    'Already Sold / Rented'
        OTHER           = 'other',           'Other'

    property    = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='reports')
    reason      = models.CharField(max_length=30, choices=Reason.choices, default=Reason.OTHER)
    description = models.TextField(blank=True, max_length=1000)
    name        = models.CharField(max_length=100, blank=True)
    email       = models.EmailField(blank=True)
    created_at  = models.DateTimeField(auto_now_add=True)
    is_reviewed = models.BooleanField(default=False)

    class Meta:
        verbose_name        = 'Property Report'
        verbose_name_plural = 'Property Reports'
        ordering            = ['-created_at']

    def __str__(self):
        return f'Report: {self.get_reason_display()} — {self.property.title}'
