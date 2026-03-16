"""
wishlist/views.py
Toggle wishlist, list saved properties.
"""
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST

from properties.models import Property
from .models import WishlistItem


@login_required
def wishlist_list(request):
    items = WishlistItem.objects.filter(user=request.user).select_related(
        'property__agent'
    ).prefetch_related('property__images')
    return render(request, 'wishlist/list.html', {'items': items})


@login_required
@require_POST
def wishlist_toggle(request, property_id):
    prop = get_object_or_404(Property, pk=property_id, status='active')
    item, created = WishlistItem.objects.get_or_create(user=request.user, property=prop)
    if not created:
        item.delete()
        saved = False
    else:
        saved = True

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({'saved': saved, 'count': request.user.wishlist.count()})
    return redirect('wishlist:list')


@login_required
@require_POST
def wishlist_remove(request, item_id):
    item = get_object_or_404(WishlistItem, pk=item_id, user=request.user)
    item.delete()
    return redirect('wishlist:list')
