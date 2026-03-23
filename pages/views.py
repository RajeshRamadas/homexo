"""
pages/views.py
Static + dynamic pages: Home, About, FAQ, EMI Calculator, Area Guides.
"""
from django.shortcuts import render, get_object_or_404
from django.http import Http404, JsonResponse
from django.db.models import Count

# ── Developer profile data (static; no DB model required) ──────────────────
_DEVELOPER_PROFILES = {
    'prestige-group': {
        'name': 'Prestige Group', 'initials': 'PS',
        'tagline': "One of India's most recognised real estate conglomerates with a 35-year legacy across residential, commercial, retail and hospitality.",
        'tags': ['Luxury', 'Residential', 'Commercial', 'Hospitality'],
        'location': 'Bengaluru · Pan India',
        'established': '1986, Bengaluru', 'workforce': '10,000+ Employees',
        'presence': 'Bengaluru, Mumbai, Hyderabad, Chennai, Goa +7',
        'listed_on': 'BSE · NSE (PRESTIGE)', 'contact': '1800-102-XXXX',
        'about_p1': "Founded in 1986 by Razack Sattar, Prestige Group has grown from a small real estate firm into one of India's most diversified property conglomerates. Headquartered in Bengaluru, the group's portfolio spans residential townships, Grade-A commercial offices, luxury retail malls, and hospitality properties across 12 cities.",
        'about_p2': "Prestige is listed on the Bombay Stock Exchange and National Stock Exchange, bringing institutional-grade governance and transparency to all its projects. Their construction arm handles over 90% of projects in-house — ensuring consistent quality from foundation to handover.",
        'about_p3': "With landmark projects like Prestige Falcon City, Prestige Lakeside Habitat, and Prestige Shantiniketan, the group has redefined urban living in South India. Their commercial arm manages over 30 million sq. ft. of leased Grade-A space, making them one of the country's largest commercial landlords.",
        'similar': [
            {'slug': 'sobha-limited',  'initials': 'SB', 'name': 'Sobha Limited',  'location': 'Bengaluru · Luxury',  'rating': '4.7'},
            {'slug': 'brigade-group',  'initials': 'BR', 'name': 'Brigade Group',  'location': 'Bengaluru · Premium', 'rating': '4.5'},
            {'slug': 'puravankara',    'initials': 'PU', 'name': 'Puravankara',    'location': 'Bengaluru · Premium', 'rating': '4.3'},
        ],
    },
    'sobha-limited': {
        'name': 'Sobha Limited', 'initials': 'SB',
        'tagline': "Renowned for its in-house construction model ensuring quality benchmarks across every stage — from architecture to interiors to civil work.",
        'tags': ['Luxury', 'Residential'],
        'location': 'Bengaluru · Pan India',
        'established': '1995, Bengaluru', 'workforce': '4,500+ Employees',
        'presence': 'Bengaluru, Gurugram, Pune, Chennai, Kochi +4',
        'listed_on': 'BSE · NSE (SOBHA)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Sobha Limited, founded in 1995 by PNC Menon, is synonymous with luxury residential construction in India. The company's unique backward-integrated model — where it controls everything from design to manufacturing of fixtures — ensures unmatched build quality.",
        'about_p2': "Listed on BSE and NSE, Sobha has delivered over 100 million sq. ft. across residential, commercial, and contractual projects. The company is particularly distinguished by its concrete-frame structures, in-house joinery, and interiors divisions.",
        'about_p3': "Sobha's projects like Sobha City, Sobha Forest Edge, and Sobha Hartland (Dubai) reflect a commitment to craftsmanship rarely seen at scale in Indian real estate.",
        'similar': [
            {'slug': 'prestige-group', 'initials': 'PS', 'name': 'Prestige Group', 'location': 'Bengaluru · Luxury',  'rating': '4.8'},
            {'slug': 'brigade-group',  'initials': 'BR', 'name': 'Brigade Group',  'location': 'Bengaluru · Premium', 'rating': '4.5'},
            {'slug': 'puravankara',    'initials': 'PU', 'name': 'Puravankara',    'location': 'Bengaluru · Premium', 'rating': '4.3'},
        ],
    },
    'godrej-properties': {
        'name': 'Godrej Properties', 'initials': 'GD',
        'tagline': "Backed by the century-old Godrej brand, bringing the highest standards of governance, sustainability and design to each project.",
        'tags': ['Premium', 'Township', 'Residential'],
        'location': 'Mumbai · Pan India',
        'established': '1990, Mumbai', 'workforce': '3,000+ Employees',
        'presence': 'Mumbai, NCR, Bengaluru, Pune, Hyderabad, Chennai',
        'listed_on': 'BSE · NSE (GODREJPROP)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Godrej Properties brings the trusted 125-year Godrej Group legacy to real estate. Established in 1990, it has grown into one of India's most active listed developers with a presence across all major metros.",
        'about_p2': "The company is known for its joint-development model that allows rapid scaling without heavy land inventory, and for strong sustainability credentials including IGBC certifications across its portfolio.",
        'about_p3': "Landmark projects include Godrej One (Vikhroli), The Trees (Vikhroli), Godrej Emerald (Thane), and Golf Links (NCR) — each reflecting thoughtful master-planning and green living principles.",
        'similar': [
            {'slug': 'prestige-group',     'initials': 'PS', 'name': 'Prestige Group',     'location': 'Bengaluru · Luxury',  'rating': '4.8'},
            {'slug': 'mahindra-lifespaces', 'initials': 'MD', 'name': 'Mahindra Lifespaces', 'location': 'Mumbai · Pan India',  'rating': '4.2'},
            {'slug': 'dlf-limited',        'initials': 'DL', 'name': 'DLF Limited',        'location': 'Delhi NCR · Luxury',  'rating': '4.4'},
        ],
    },
    'brigade-group': {
        'name': 'Brigade Group', 'initials': 'BR',
        'tagline': "Synonymous with integrated townships and world-class commercial spaces. Their Gateway projects have redefined Bengaluru's skyline.",
        'tags': ['Premium', 'Commercial', 'Residential'],
        'location': 'Bengaluru · South India',
        'established': '1986, Bengaluru', 'workforce': '5,000+ Employees',
        'presence': 'Bengaluru, Chennai, Hyderabad, Mysuru, Kochi',
        'listed_on': 'BSE · NSE (BRIGADE)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Brigade Group, founded in 1986 by M.R. Jaishankar, is one of South India's leading real estate developers. The company has built landmark mixed-use developments that combine residences, offices, retail, and hospitality under one master-plan.",
        'about_p2': "Their flagship Brigade Gateway, World Trade Center Bengaluru, and Brigade Orchards townships have set new benchmarks for integrated urban living.",
        'about_p3': "Brigade's retail arm manages 5+ million sq. ft. of mall space, while the hospitality vertical operates 3,000+ hotel keys across South India.",
        'similar': [
            {'slug': 'prestige-group', 'initials': 'PS', 'name': 'Prestige Group', 'location': 'Bengaluru · Luxury',  'rating': '4.8'},
            {'slug': 'sobha-limited',  'initials': 'SB', 'name': 'Sobha Limited',  'location': 'Bengaluru · Luxury',  'rating': '4.7'},
            {'slug': 'puravankara',    'initials': 'PU', 'name': 'Puravankara',    'location': 'Bengaluru · Premium', 'rating': '4.3'},
        ],
    },
    'mahindra-lifespaces': {
        'name': 'Mahindra Lifespaces', 'initials': 'MD',
        'tagline': "India's first carbon-neutral developer delivering sustainable, affordable homes and integrated industrial clusters.",
        'tags': ['Affordable', 'Green Certified'],
        'location': 'Mumbai · Pan India',
        'established': '1994, Mumbai', 'workforce': '1,200+ Employees',
        'presence': 'Mumbai, NCR, Chennai, Pune, Bengaluru, Nagpur',
        'listed_on': 'BSE · NSE (MAHLIFESPA)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Mahindra Lifespace Developers Ltd is the real estate and infrastructure development arm of the USD 21 billion Mahindra Group. They pioneered the 'green homes' movement in India and became the first Indian developer to achieve carbon neutrality.",
        'about_p2': "The company develops across two business lines: Mahindra Lifespaces (residential) targeting mid-income and affordable buyers, and Mahindra World City (integrated industrial townships).",
        'about_p3': "Mahindra World City campuses in Chennai and Jaipur house global companies including BMW, Infosys, and Capgemini, while their residential projects consistently top sustainability rankings.",
        'similar': [
            {'slug': 'godrej-properties', 'initials': 'GD', 'name': 'Godrej Properties', 'location': 'Mumbai · Premium', 'rating': '4.5'},
            {'slug': 'oberoi-realty',     'initials': 'OR', 'name': 'Oberoi Realty',     'location': 'Mumbai · Luxury',  'rating': '4.6'},
            {'slug': 'sunteck-realty',    'initials': 'SN', 'name': 'Sunteck Realty',    'location': 'Mumbai · MMR',     'rating': '4.2'},
        ],
    },
    'dlf-limited': {
        'name': 'DLF Limited', 'initials': 'DL',
        'tagline': "India's largest listed real estate company with a 75-year legacy. DLF has shaped Gurgaon's landscape and sets the benchmark for luxury in North India.",
        'tags': ['Luxury', 'Commercial', 'Residential'],
        'location': 'Delhi NCR · Pan India',
        'established': '1946, Delhi', 'workforce': '25,000+ Employees',
        'presence': 'Delhi NCR, Mumbai, Chennai, Kolkata, Chandigarh +8',
        'listed_on': 'BSE · NSE (DLF)', 'contact': '1800-XXX-XXXX',
        'about_p1': "DLF Limited is India's largest listed real estate developer with a 75-year track record. Founded by Chaudhary Raghvendra Singh in 1946, DLF was instrumental in developing Gurugram (Gurgaon) from agricultural land into India's premier corporate hub.",
        'about_p2': "Their commercial arm — DLF Cyber City Developers — manages over 40 million sq. ft. of premium office space leased to global companies including Google, Amazon, and Microsoft.",
        'about_p3': "On the residential side, DLF's ultra-luxury brand 'The Crest', '5S' and 'Camellias' projects in DLF-5, Gurugram are benchmarks for high-end living in North India.",
        'similar': [
            {'slug': 'godrej-properties', 'initials': 'GD', 'name': 'Godrej Properties', 'location': 'Mumbai · Premium', 'rating': '4.5'},
            {'slug': 'oberoi-realty',     'initials': 'OR', 'name': 'Oberoi Realty',     'location': 'Mumbai · Luxury',  'rating': '4.6'},
            {'slug': 'k-raheja-corp',     'initials': 'KP', 'name': 'K Raheja Corp',     'location': 'Mumbai · Premium', 'rating': '4.3'},
        ],
    },
    'puravankara': {
        'name': 'Puravankara', 'initials': 'PU',
        'tagline': "Serving both premium and affordable segments. A trusted name for consistent quality and on-time delivery in South India.",
        'tags': ['Premium', 'Affordable'],
        'location': 'Bengaluru · South India',
        'established': '1975, Bengaluru', 'workforce': '3,500+ Employees',
        'presence': 'Bengaluru, Chennai, Hyderabad, Kochi, Mumbai, Pune',
        'listed_on': 'BSE · NSE (PURAVANKARA)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Puravankara Limited, established in 1975, is one of South India's most trusted real estate companies. The company operates two distinct brands: Puravankara (premium) and Provident (affordable), catering to a wide spectrum of homebuyers.",
        'about_p2': "With over 80 residential and commercial projects completed spanning 60+ million sq. ft., Puravankara has a consistent track record of timely delivery and quality construction.",
        'about_p3': "Their Provident brand has become particularly strong in the affordable segment, bringing lifestyle amenities to budget-conscious buyers in Bengaluru, Chennai, and Hyderabad.",
        'similar': [
            {'slug': 'prestige-group', 'initials': 'PS', 'name': 'Prestige Group', 'location': 'Bengaluru · Luxury',  'rating': '4.8'},
            {'slug': 'sobha-limited',  'initials': 'SB', 'name': 'Sobha Limited',  'location': 'Bengaluru · Luxury',  'rating': '4.7'},
            {'slug': 'brigade-group',  'initials': 'BR', 'name': 'Brigade Group',  'location': 'Bengaluru · Premium', 'rating': '4.5'},
        ],
    },
    'oberoi-realty': {
        'name': 'Oberoi Realty', 'initials': 'OR',
        'tagline': "Synonymous with ultra-luxury living in Mumbai. Iconic Elysian, Sky City and Three Sixty West projects redefine high-rise opulence.",
        'tags': ['Luxury', 'Ultra Premium'],
        'location': 'Mumbai',
        'established': '1998, Mumbai', 'workforce': '2,000+ Employees',
        'presence': 'Mumbai (Goregaon, Borivali, Worli, Mulund)',
        'listed_on': 'BSE · NSE (OBEROIRLTY)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Oberoi Realty is Mumbai's pre-eminent ultra-luxury developer, known for creating self-contained townships with unparalleled amenities. Founded by Vikas Oberoi, the company operates exclusively in Mumbai's premium micro-markets.",
        'about_p2': "Their Oberoi Garden City in Goregaon spans 80 acres and includes the Oberoi Mall, Westin Mumbai, and multiple residential towers — a city within a city.",
        'about_p3': "Three Sixty West — a collaboration with Hilton on Worli Seaface — and Sky City in Borivali represent the pinnacle of Mumbai luxury, targeting HNI buyers and NRI investors.",
        'similar': [
            {'slug': 'dlf-limited',    'initials': 'DL', 'name': 'DLF Limited',    'location': 'Delhi NCR · Luxury', 'rating': '4.4'},
            {'slug': 'k-raheja-corp',  'initials': 'KP', 'name': 'K Raheja Corp',  'location': 'Mumbai · Premium',  'rating': '4.3'},
            {'slug': 'sunteck-realty', 'initials': 'SN', 'name': 'Sunteck Realty', 'location': 'Mumbai · MMR',      'rating': '4.2'},
        ],
    },
    'k-raheja-corp': {
        'name': 'K Raheja Corp', 'initials': 'KP',
        'tagline': "Known for landmark commercial hubs and premium residential towers across Mumbai and Pune's prime micro-markets.",
        'tags': ['Premium', 'Commercial'],
        'location': 'Mumbai · Pune',
        'established': '1956, Mumbai', 'workforce': '3,000+ Employees',
        'presence': 'Mumbai, Pune, Hyderabad',
        'listed_on': 'Privately Held', 'contact': '1800-XXX-XXXX',
        'about_p1': "K. Raheja Corp is one of Mumbai's oldest and most respected real estate groups. Founded in 1956, the group has deep roots in the city's commercial real estate — developing iconic office complexes and retail malls that became defining landmarks.",
        'about_p2': "Their retail brand Shoppers Stop is listed on the NSE, while their commercial developments — Mindspace Business Parks — span Hyderabad, Mumbai, Pune, and Chennai with 32+ million sq. ft. of Grade-A office space.",
        'about_p3': "On the residential front, K. Raheja Corp projects in Juhu, Sion, Worli, and Bandra cater to Mumbai's affluent buyers seeking centrally located, thoughtfully designed homes.",
        'similar': [
            {'slug': 'oberoi-realty',  'initials': 'OR', 'name': 'Oberoi Realty',  'location': 'Mumbai · Luxury',  'rating': '4.6'},
            {'slug': 'sunteck-realty', 'initials': 'SN', 'name': 'Sunteck Realty', 'location': 'Mumbai · MMR',     'rating': '4.2'},
            {'slug': 'dlf-limited',    'initials': 'DL', 'name': 'DLF Limited',    'location': 'Delhi NCR · Luxury', 'rating': '4.4'},
        ],
    },
    'sunteck-realty': {
        'name': 'Sunteck Realty', 'initials': 'SN',
        'tagline': "Catering to multiple buyer segments, from ultra-luxury BKC projects to affordable homes in the western suburbs of Mumbai.",
        'tags': ['Premium', 'Affordable'],
        'location': 'Mumbai · MMR',
        'established': '2008, Mumbai', 'workforce': '1,500+ Employees',
        'presence': 'Mumbai (BKC, Goregaon, Vasai, Naigaon, Kalyan)',
        'listed_on': 'BSE · NSE (SUNTECK)', 'contact': '1800-XXX-XXXX',
        'about_p1': "Sunteck Realty, listed in 2009, has rapidly grown into a diversified Mumbai developer covering ultra-luxury, premium, and affordable segments — a rare feat in a market typically dominated by segment-specific players.",
        'about_p2': "Their Signature — One BKC project in the heart of Mumbai's financial district is among India's most prestigious commercial addresses, while Sunteck City in Goregaon offers premium residences with a resort lifestyle.",
        'about_p3': "In the affordable segment, Sunteck's Vasai and Naigaon projects have been consistently popular among first-time Mumbai buyers seeking good connectivity and value-for-money specifications.",
        'similar': [
            {'slug': 'oberoi-realty',     'initials': 'OR', 'name': 'Oberoi Realty',     'location': 'Mumbai · Luxury',  'rating': '4.6'},
            {'slug': 'k-raheja-corp',     'initials': 'KP', 'name': 'K Raheja Corp',     'location': 'Mumbai · Premium', 'rating': '4.3'},
            {'slug': 'mahindra-lifespaces','initials': 'MD', 'name': 'Mahindra Lifespaces','location': 'Mumbai · Affordable','rating': '4.2'},
        ],
    },
}

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
        ).prefetch_related('categories').order_by('-published_at')[:5],

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


def contact(request):
    return render(request, 'pages/contact.html')


def area_guides(request):
    return render(request, 'pages/area_guides.html')


def market_reports(request):
    reports = Post.objects.filter(
        status='published', categories__slug='market-reports'
    ).distinct().order_by('-published_at')[:12]
    return render(request, 'pages/market_reports.html', {'reports': reports})


def developers(request):
    """Property Developers directory page."""
    return render(request, 'pages/developers.html')


def developer_profile(request, slug):
    """Single developer profile page."""
    developer = _DEVELOPER_PROFILES.get(slug)
    if not developer:
        raise Http404
    # Split name for italic-last-word styling in template
    parts = developer['name'].rsplit(' ', 1)
    developer = dict(developer)
    developer['name_first'] = parts[0] if len(parts) > 1 else developer['name']
    developer['name_last']  = parts[1] if len(parts) > 1 else ''
    return render(request, 'pages/developer_profile.html', {'developer': developer})


def security(request):
    """Home security services landing page."""
    return render(request, 'pages/security.html')


def home_service(request):
    """Home maintenance and services landing page."""
    return render(request, 'pages/home_service.html')


def legal(request):
    """Dedicated property legal services landing page."""
    return render(request, 'pages/legal.html')


def legal_homeloan(request):
    """Combined property legal and home loan landing page."""
    return render(request, 'pages/legal_homeloan.html')


def home_loan(request):
    """Dedicated home loan landing page."""
    return render(request, 'pages/home_loan.html')


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
