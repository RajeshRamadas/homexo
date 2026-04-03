"""
properties/views.py
List, detail, create, update, delete views for properties.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.core.paginator import Paginator
import datetime
from django.forms import inlineformset_factory
from django.views.generic import DetailView

from .models import Property, PropertyTag, PropertyImage, PropertyFloorPlan, PropertyFeature
from .forms import PropertySearchForm, PropertyCreateForm
try:
    from properties.models import Developer
except ImportError:
    Developer = None

# Inline formset for amenities / features (used by create & update views)
PropertyFeatureFormSet = inlineformset_factory(
    Property, PropertyFeature,
    fields=('name', 'icon_image'),
    extra=6, can_delete=True,
)


def property_list(request):
    """Main listing page with search & filters."""
    qs = Property.objects.filter(status='active').select_related('developer').prefetch_related('images', 'tags')

    form = PropertySearchForm(request.GET or None)

    # ── Filters ───────────────────────────────────────────────────────────────
    listing_type = request.GET.get('type', '')
    location     = request.GET.get('location', '').strip()
    prop_type    = request.GET.get('property_type', '')
    bhk          = request.GET.get('bhk', '')
    price_range  = request.GET.get('price', '')

    if listing_type:
        qs = qs.filter(listing_type=listing_type)

    if location:
        # Handle common city name aliases (e.g., Bangalore ↔ Bengaluru)
        CITY_ALIASES = {
            'bangalore': 'bengaluru',
            'bengaluru': 'bangalore',
            'bombay':    'mumbai',
            'mumbai':    'bombay',
            'madras':    'chennai',
            'chennai':   'madras',
            'calcutta':  'kolkata',
            'kolkata':   'calcutta',
        }
        alias = CITY_ALIASES.get(location.lower(), '')
        location_q = (
            Q(locality__icontains=location) |
            Q(city__icontains=location) |
            Q(address__icontains=location)
        )
        if alias:
            location_q |= (
                Q(locality__icontains=alias) |
                Q(city__icontains=alias) |
                Q(address__icontains=alias)
            )
        qs = qs.filter(location_q)

    if prop_type:
        qs = qs.filter(property_type=prop_type)

    if bhk:
        qs = qs.filter(bhk=bhk)

    PRICE_RANGES = {
        'under50l':   (0,        50_00_000),
        '50l-1cr':    (50_00_000, 1_00_00_000),
        '1cr-3cr':    (1_00_00_000, 3_00_00_000),
        '3cr-10cr':   (3_00_00_000, 10_00_00_000),
        'above10cr':  (10_00_00_000, None),
    }
    if price_range in PRICE_RANGES:
        low, high = PRICE_RANGES[price_range]
        qs = qs.filter(price__gte=low)
        if high:
            qs = qs.filter(price__lte=high)

    # ── Area range ────────────────────────────────────────────────────────────
    area_min = request.GET.get('area_min', '').strip()
    area_max = request.GET.get('area_max', '').strip()
    if area_min.isdigit():
        qs = qs.filter(area_sqft__gte=int(area_min))
    if area_max.isdigit():
        qs = qs.filter(area_sqft__lte=int(area_max))

    # ── Property Age ──────────────────────────────────────────────────────────
    age = request.GET.get('age', '')
    AGE_MAP = {'1': 1, '3': 3, '5': 5, '10': 10}
    if age in AGE_MAP:
        qs = qs.filter(age_years__lte=AGE_MAP[age])

    # ── Bathrooms ─────────────────────────────────────────────────────────────
    baths = request.GET.get('baths', '')
    if baths.isdigit():
        qs = qs.filter(bathrooms__gte=int(baths))

    # ── Furnishing ────────────────────────────────────────────────────────────
    furnishing_filter = request.GET.get('furnishing', '')
    if furnishing_filter:
        qs = qs.filter(furnishing=furnishing_filter)

    # ── Floor ─────────────────────────────────────────────────────────────────
    floor = request.GET.get('floor', '')
    FLOOR_RANGES = {
        'ground': (0, 0),
        '1-3':    (1, 3),
        '4-6':    (4, 6),
        '7-9':    (7, 9),
        '10+':    (10, None),
    }
    if floor in FLOOR_RANGES:
        f_low, f_high = FLOOR_RANGES[floor]
        qs = qs.filter(floor_no__gte=f_low)
        if f_high is not None:
            qs = qs.filter(floor_no__lte=f_high)

    # ── Construction Status ───────────────────────────────────────────────────
    con_status = request.GET.get('con_status', '')
    if con_status:
        qs = qs.filter(construction_status=con_status)

    # ── With Photo ────────────────────────────────────────────────────────────
    with_photo = request.GET.get('with_photo', '')
    if with_photo == '1':
        qs = qs.filter(images__isnull=False).distinct()

    # ── New only ──────────────────────────────────────────────────────────────
    only_new = request.GET.get('is_new', '')
    if only_new == '1':
        qs = qs.filter(is_new=True)

    # ── Parking ───────────────────────────────────────────────────────────────
    parking = request.GET.get('parking', '')
    if parking == '2w':
        qs = qs.filter(two_wheeler_parking=True)
    elif parking == '4w':
        qs = qs.filter(four_wheeler_parking=True)

    # ── Developer filter (from developer profile page link) ───────────────────
    developer_slug = request.GET.get('developer', '').strip()
    active_developer = None
    if developer_slug and Developer:
        try:
            active_developer = Developer.objects.get(slug=developer_slug)
            qs = qs.filter(developer=active_developer)
        except Developer.DoesNotExist:
            pass

    # ── Sorting ───────────────────────────────────────────────────────────────
    sort = request.GET.get('sort', 'newest')
    sort_options = {
        'price_asc':  'price',
        'price_desc': '-price',
        'newest':     '-created_at',
        'popular':    '-views_count',
    }
    qs = qs.order_by(sort_options.get(sort, '-created_at'))

    paginator = Paginator(qs, 12)
    page      = request.GET.get('page')
    properties = paginator.get_page(page)

    page_range = paginator.get_elided_page_range(
        properties.number, on_each_side=2, on_ends=1
    )

    context = {
        'properties':       properties,
        'form':             form,
        'total':            paginator.count,
        'listing_type':     listing_type,
        'current_sort':     sort,
        'tags':             PropertyTag.objects.all(),
        'page_range':       page_range,
        'ELLIPSIS':         paginator.ELLIPSIS,
        'active_developer': active_developer,
    }
    return render(request, 'properties/list.html', context)


def property_detail(request, slug):
    """Single property detail page."""
    prop = get_object_or_404(Property, slug=slug, status='active')
    prop.increment_views()

    similar_qs = Property.objects.filter(
        status='active',
        listing_type=prop.listing_type,
        city=prop.city,
    ).exclude(pk=prop.pk).order_by('-created_at')[:3]

    similar = list(similar_qs)
    if len(similar) < 3:
        needed = 3 - len(similar)
        existing_ids = [p.pk for p in similar] + [prop.pk]
        fallback = Property.objects.filter(
            status='active'
        ).exclude(pk__in=existing_ids).order_by('-views_count')[:needed]
        similar.extend(list(fallback))

    is_saved = False
    if request.user.is_authenticated:
        from wishlist.models import WishlistItem
        is_saved = WishlistItem.objects.filter(user=request.user, property=prop).exists()

    context = {
        'property': prop,
        'similar':  similar,
        'images':   prop.images.all(),
        'features': prop.features.all(),
        'connectivity': prop.connectivity.all(),
        'is_saved': is_saved,
    }
    return render(request, 'properties/detail.html', context)


@login_required
def property_create(request):
    """List a new property (requires login)."""
    form = PropertyCreateForm(request.POST or None, request.FILES or None)
    feature_formset = PropertyFeatureFormSet(request.POST or None, request.FILES or None, prefix='features')
    if request.method == 'POST' and form.is_valid() and feature_formset.is_valid():
        prop = form.save(commit=False)
        prop.owner = request.user
        prop.status = 'pending'  # Requires admin approval
        prop.save()
        form.save_m2m()
        # Save uploaded images
        for i, img_file in enumerate(request.FILES.getlist('prop_images')):
            PropertyImage.objects.create(
                property=prop, image=img_file, is_primary=(i == 0)
            )
        # Save floor plan images
        for i, fp_file in enumerate(request.FILES.getlist('floor_plans')):
            PropertyFloorPlan.objects.create(property=prop, image=fp_file, order=i)
        # Save features
        feature_formset.instance = prop
        feature_formset.save()
        messages.success(request, 'Your property has been submitted for review.')
        return redirect('properties:detail', slug=prop.slug)

    return render(request, 'properties/create.html', {
        'form': form,
        'feature_formset': feature_formset,
    })


@login_required
def property_update(request, slug):
    prop = get_object_or_404(Property, slug=slug)
    # Allow the owner OR any staff member to edit
    if prop.owner != request.user and not request.user.is_staff:
        raise PermissionDenied

    form = PropertyCreateForm(request.POST or None, request.FILES or None, instance=prop)
    feature_formset = PropertyFeatureFormSet(
        request.POST or None, request.FILES or None, instance=prop, prefix='features'
    )
    if request.method == 'POST' and form.is_valid() and feature_formset.is_valid():
        form.save()
        # Delete floor plans that were checked for removal
        delete_fp_ids = request.POST.getlist('delete_floor_plan')
        if delete_fp_ids:
            PropertyFloorPlan.objects.filter(pk__in=delete_fp_ids, property=prop).delete()
        # Add any newly uploaded floor plan images
        existing_fp_count = prop.floor_plans.count()
        for i, fp_file in enumerate(request.FILES.getlist('floor_plans')):
            PropertyFloorPlan.objects.create(
                property=prop, image=fp_file, order=existing_fp_count + i
            )
        # Delete images that were checked for removal
        delete_ids = request.POST.getlist('delete_image')
        if delete_ids:
            PropertyImage.objects.filter(pk__in=delete_ids, property=prop).delete()
        # Add any newly uploaded images
        existing_count = prop.images.count()
        for i, img_file in enumerate(request.FILES.getlist('prop_images')):
            PropertyImage.objects.create(
                property=prop, image=img_file,
                is_primary=(existing_count == 0 and i == 0)
            )
        feature_formset.save()
        messages.success(request, 'Property updated successfully.')
        return redirect('properties:detail', slug=prop.slug)

    return render(request, 'properties/update.html', {
        'form': form,
        'property': prop,
        'feature_formset': feature_formset,
        'existing_images': prop.images.all(),
        'existing_floor_plans': prop.floor_plans.all(),
    })


@login_required
def property_delete(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    if request.method == 'POST':
        prop.delete()
        messages.success(request, 'Property listing removed.')
        return redirect('pages:home')
    return render(request, 'properties/confirm_delete.html', {'property': prop})


def featured_properties(request):
    """API-style endpoint for featured carousel — returns JSON."""
    from django.http import JsonResponse
    props = Property.objects.filter(status='active', is_featured=True).values(
        'id', 'title', 'slug', 'price', 'price_label', 'locality', 'city',
        'bedrooms', 'bathrooms', 'area_sqft',
    )[:6]
    return JsonResponse({'properties': list(props)})
