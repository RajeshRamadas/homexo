"""
properties/views.py
List, detail, create, update, delete views for properties.
"""

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from django.views.generic import DetailView

from .models import Property, PropertyTag
from .forms import PropertySearchForm, PropertyCreateForm


def property_list(request):
    """Main listing page with search & filters."""
    qs = Property.objects.filter(status='active').select_related('agent').prefetch_related('images', 'tags')

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
        qs = qs.filter(
            Q(locality__icontains=location) |
            Q(city__icontains=location) |
            Q(address__icontains=location)
        )

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

    # ── Sorting ───────────────────────────────────────────────────────────────
    sort = request.GET.get('sort', '-created_at')
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
        'properties':    properties,
        'form':          form,
        'total':         paginator.count,
        'listing_type':  listing_type,
        'current_sort':  sort,
        'tags':          PropertyTag.objects.all(),
        'page_range':    page_range,
        'ELLIPSIS':      paginator.ELLIPSIS,
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

    context = {
        'property': prop,
        'similar':  similar,
        'images':   prop.images.all(),
        'features': prop.features.all(),
    }
    return render(request, 'properties/detail.html', context)


@login_required
def property_create(request):
    """List a new property (requires login)."""
    form = PropertyCreateForm(request.POST or None, request.FILES or None)
    if request.method == 'POST' and form.is_valid():
        prop = form.save(commit=False)
        prop.owner = request.user
        prop.status = 'pending'  # Requires admin approval
        prop.save()
        form.save_m2m()
        messages.success(request, 'Your property has been submitted for review.')
        return redirect('properties:detail', slug=prop.slug)

    return render(request, 'properties/create.html', {'form': form})


@login_required
def property_update(request, slug):
    prop = get_object_or_404(Property, slug=slug, owner=request.user)
    form = PropertyCreateForm(request.POST or None, request.FILES or None, instance=prop)
    if request.method == 'POST' and form.is_valid():
        form.save()
        messages.success(request, 'Property updated successfully.')
        return redirect('properties:detail', slug=prop.slug)

    return render(request, 'properties/update.html', {'form': form, 'property': prop})


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
