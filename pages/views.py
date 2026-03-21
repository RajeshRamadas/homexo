"""
pages/views.py
Static + dynamic pages: Home, About, FAQ, EMI Calculator, Area Guides.
"""
from django.shortcuts import render
from django.http import JsonResponse
from django.db.models import Count

from properties.models import Property
from agents.models import Agent
from blog.models import Post
from testimonials.models import Testimonial
from enquiries.forms import EnquiryForm


def home(request):
    """Homepage — assembles all sections from the HOMEXO HTML design."""

    # Count active properties per listing type for search tab badges
    type_counts = {
        item['listing_type']: item['count']
        for item in Property.objects.filter(status='active')
                                    .values('listing_type')
                                    .annotate(count=Count('id'))
    }

    total_active = Property.objects.filter(status='active').count()
    total_agents = Agent.objects.filter(is_active=True, is_verified=True).count()
    total_cities  = Property.objects.filter(status='active').values('city').distinct().count()

    context = {
        # Search form tabs
        'listing_types': Property.ListingType.choices,
        'property_types': Property.PropertyType.choices,
        'bhk_choices': Property.BHK.choices,
        'type_counts': type_counts,

        # Signature / ultra-premium collection (top 3)
        'signature_properties': Property.objects.filter(
            status='active', is_signature=True
        ).prefetch_related('images').order_by('-created_at')[:3],

        # Featured slider (6 cards)
        'featured_properties': Property.objects.filter(
            status='active', is_featured=True
        ).prefetch_related('images', 'tags').order_by('-created_at')[:6],

        # Agents strip (4 highlighted)
        'agents': Agent.objects.filter(
            is_active=True, is_verified=True
        ).select_related('user').order_by('-rating')[:4],

        # Testimonials carousel
        'testimonials': Testimonial.objects.filter(is_active=True).order_by('order')[:6],

        # News carousel (5 latest posts)
        'news_posts': Post.objects.filter(
            status='published'
        ).select_related('category').order_by('-published_at')[:5],

        # Popular cities for search chips (top cities by listing count)
        'popular_cities': (
            Property.objects.filter(status='active')
            .values_list('city', flat=True)
            .order_by('city')
            .distinct()[:8]
        ),

        # CTA / contact enquiry form
        'enquiry_form': EnquiryForm(),

        # Stats for animated counters
        'stats': {
            'properties':   total_active or 1200,
            'happy_clients': max(total_active * 4, 4800),
            'cities':       total_cities or 12,
            'agents':       total_agents or 48,
            'years':        10,
        },
    }
    return render(request, 'pages/home.html', context)


def about(request):
    agents = Agent.objects.filter(is_active=True, is_verified=True).select_related('user')[:8]
    return render(request, 'pages/about.html', {'agents': agents})


def faq(request):
    return render(request, 'pages/faq.html')


def area_guides(request):
    return render(request, 'pages/area_guides.html')


def market_reports(request):
    reports = Post.objects.filter(
        status='published', category__slug='market-reports'
    ).order_by('-published_at')[:12]
    return render(request, 'pages/market_reports.html', {'reports': reports})


def emi_calculator(request):
    """Renders the EMI calculator page."""
    return render(request, 'pages/emi_calculator.html')


def emi_calculate_api(request):
    """
    GET /emi/calculate/?principal=5000000&rate=8.5&tenure=240
    Returns monthly EMI as JSON.
    """
    try:
        principal = float(request.GET.get('principal', 0))
        annual_rate = float(request.GET.get('rate', 0))
        tenure_months = int(request.GET.get('tenure', 0))

        if not all([principal, annual_rate, tenure_months]):
            return JsonResponse({'error': 'Missing parameters.'}, status=400)

        monthly_rate = annual_rate / (12 * 100)

        # Standard EMI formula: P * r * (1+r)^n / ((1+r)^n - 1)
        factor = (1 + monthly_rate) ** tenure_months
        emi = principal * monthly_rate * factor / (factor - 1)

        total_payment  = emi * tenure_months
        total_interest = total_payment - principal

        return JsonResponse({
            'emi':            round(emi, 2),
            'total_payment':  round(total_payment, 2),
            'total_interest': round(total_interest, 2),
            'principal':      principal,
        })
    except (ValueError, ZeroDivisionError) as e:
        return JsonResponse({'error': str(e)}, status=400)
