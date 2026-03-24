from django.db import migrations


def create_apartment_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    CampaignHighlight = apps.get_model('campaigns', 'CampaignHighlight')
    CampaignFloorPlan = apps.get_model('campaigns', 'CampaignFloorPlan')
    CampaignAmenity = apps.get_model('campaigns', 'CampaignAmenity')

    defaults = {
        'title': 'Prestige Horizon Grand',
        'developer_name': 'Prestige Group',
        'accent_color': '#C9944A',
        'nav_style': 'branded',
        'nav_cta_text': 'Book a Site Visit',
        'nav_show_links': True,

        # Hero
        'hero_heading': 'Prestige Horizon Grand|Whitefield, Bangalore',
        'hero_sub': (
            'Ultra-premium 2, 3 & 4 BHK residences across 18 acres with panoramic '
            'skyline views, resort-grade amenities and direct ORR connectivity. '
            'Booking open — limited pre-launch inventory.'
        ),

        # Key stats
        'stat_land_parcel': '18 Acres',
        'stat_floors': '2B + G + 32',
        'stat_configs': '2, 3 & 4 BHK',
        'stat_possession': 'Mar 2029+',
        'stat_price_start': '\u20b91.45 Crore Onwards*',

        # Offer
        'offer_label': 'Pre-Launch Advantage \u00b7 No Pre-EMI for 24 months',

        # About
        'about_heading': 'A New Landmark on the Whitefield Skyline',
        'about_body': (
            'Prestige Horizon Grand is conceived as Whitefield\u2019s most '
            'aspirational address \u2014 a gated 18-acre enclave of towers that '
            'rise 32 storeys above landscaped podiums, each oriented for '
            'maximum light, ventilation and unobstructed views.\n\n'
            'The master plan dedicates over 70% of the land to open greens, '
            'water features and recreational zones. A 45,000 sq.ft. clubhouse '
            'anchors the lifestyle offering with an infinity-edge pool, sky '
            'lounge, co-working suites and a curated wellness floor.\n\n'
            'Every apartment ships with imported marble flooring, VRV air-'
            'conditioning, smart-home pre-wiring and German-engineered kitchen '
            'modules \u2014 a specification usually reserved for penthouses.'
        ),

        # Master plan
        'masterplan_heading': 'Overall Master Plan \u2014 Prestige Horizon Grand',
        'masterplan_body': (
            'Explore the community layout \u2014 tower orientation, podium gardens, '
            'vehicular-free zones and amenity clusters planned for walkable convenience. '
            'Request the detailed brochure for exact tower positioning and unit availability.'
        ),

        # Location
        'location_heading': 'Prestige Horizon Grand \u2014 Whitefield, Bangalore',
        'location_body': (
            'Road Connectivity: Direct access to the Outer Ring Road via a '
            'dedicated service road; Whitefield Main Road and Old Airport Road '
            'within 10 minutes.\n\n'
            'Metro Access: Kadugodi Metro Station (Purple Line extension) is '
            'approximately 2.5 km \u2014 under 5 minutes by car.\n\n'
            'Airport Route: Kempegowda International Airport via the elevated '
            'expressway corridor \u2014 approximately 55 minutes.\n\n'
            'IT Hubs: ITPL, RMZ Ecoworld, Embassy Tech Village, Bagmane Tech '
            'Park and Prestige Tech Park are all within a 6 km radius.\n\n'
            'Schools: National Public School, Inventure Academy, Greenwood High '
            'and Deens Academy are within a 5 km catchment.\n\n'
            'Healthcare: Columbia Asia, Narayana Multispeciality and Manipal '
            'Hospital Whitefield \u2014 all under 4 km.\n\n'
            'Shopping & Leisure: Phoenix Marketcity, VR Bengaluru and Forum '
            'Neighbourhood Mall are 5\u201310 minutes away.'
        ),

        # CTA
        'cta_heading': 'Secure Your Address at Pre-Launch Pricing',
        'cta_sub': (
            'EOI spots are limited. Pay \u20b92L to lock today\u2019s price and '
            'choose your preferred floor & view before public release.'
        ),
        'cta_button_text': 'Reserve Now \u2014 \u20b92L EOI',

        # Disclaimer
        'disclaimer': (
            'We are an authorised channel partner for this project. Content is '
            'provided by the developer and is for informational purposes only. '
            'It does not constitute an offer or contract. Prices mentioned are '
            'tentative, subject to change without prior notice, and do not include '
            'registration, GST, or other statutory charges. Images and renders are '
            'artist impressions. RERA registration details available on request.'
        ),

        # Footer
        'footer_style': 'branded',
        'footer_tagline': 'Prestige Group \u00b7 Horizon Grand Collection',
        'footer_address': 'HOMEXO Experience Centre, Ground Floor, Brigade Gateway, Rajajinagar, Bangalore 560055',
        'footer_email': 'horizon@homexo.com',
        'footer_phone': '+91 80 4567 8900',
    }

    campaign, created = Campaign.objects.get_or_create(
        slug='prestige-horizon-grand',
        defaults=defaults,
    )
    if not created:
        for field, value in defaults.items():
            setattr(campaign, field, value)
        campaign.save(update_fields=list(defaults.keys()))

    # ── Highlights ────────────────────────────────────────────────────
    campaign.highlights.all().delete()
    highlights = [
        {'icon': '🏗️', 'heading': 'Pre-launch pricing advantage',
         'body': 'Lock in today\'s rate before public release \u2014 historically 12\u201318% below post-launch pricing.'},
        {'icon': '🌳', 'heading': '70% open & green space',
         'body': 'Podium-level parks, water courts, jogging loops and a central meadow spanning 4 acres.'},
        {'icon': '🏊', 'heading': '45,000 sq.ft. clubhouse',
         'body': 'Infinity pool, sky lounge, spa, co-work pods, indoor sports courts and a rooftop observatory.'},
        {'icon': '🚇', 'heading': 'Metro in 5 minutes',
         'body': 'Kadugodi Metro (Purple Line) at 2.5 km; ITPL and ORR tech belt within a 6 km radius.'},
        {'icon': '🏠', 'heading': 'German kitchen & VRV AC',
         'body': 'Imported marble, VRV air-conditioning, smart-home wiring and Grohe fittings as standard.'},
        {'icon': '📜', 'heading': 'RERA registered & bank approved',
         'body': 'Pre-approved by SBI, HDFC, ICICI and Axis; construction-linked payment plan available.'},
    ]
    for order, data in enumerate(highlights, 1):
        CampaignHighlight.objects.create(campaign=campaign, order=order, **data)

    # ── Floor Plans ───────────────────────────────────────────────────
    campaign.floor_plans.all().delete()
    floor_plans = [
        {'config': '2 BHK Standard',  'sba_range': '1150 \u2013 1200 sft', 'price_range': '\u20b91.45 \u2013 1.60 Cr*'},
        {'config': '2 BHK Large',     'sba_range': '1350 sft',             'price_range': '\u20b91.72 \u2013 1.85 Cr*'},
        {'config': '3 BHK Standard',  'sba_range': '1650 \u2013 1700 sft', 'price_range': '\u20b92.20 \u2013 2.40 Cr*'},
        {'config': '3 BHK Large',     'sba_range': '1950 sft',             'price_range': '\u20b92.65 \u2013 2.85 Cr*'},
        {'config': '3.5 BHK Premium', 'sba_range': '2200 \u2013 2300 sft', 'price_range': '\u20b93.10 \u2013 3.40 Cr*'},
        {'config': '4 BHK Penthouse', 'sba_range': '2850 \u2013 3100 sft', 'price_range': '\u20b94.25 \u2013 4.80 Cr*'},
    ]
    for order, data in enumerate(floor_plans, 1):
        CampaignFloorPlan.objects.create(campaign=campaign, order=order, **data)

    # ── Amenities ─────────────────────────────────────────────────────
    campaign.amenities.all().delete()
    amenities = [
        {'icon': '🏋️', 'name': 'High-Performance Fitness Studio',
         'description': 'Pro-grade strength & cardio zones, personal training bays, and TRX / CrossFit areas.'},
        {'icon': '🏊', 'name': 'Temperature-Controlled Infinity Pool',
         'description': 'Resort-style pool with loungers, a kids\' splash zone and landscaped cabana decks.'},
        {'icon': '🏸', 'name': 'Sports Courts & Active Zones',
         'description': 'Badminton, basketball, tennis and a 200m jogging track around the central meadow.'},
        {'icon': '🍸', 'name': 'Sky Lounge & Rooftop Bar',
         'description': 'A 32nd-floor lounge with panoramic city views, private dining and a stargazing deck.'},
        {'icon': '👶', 'name': 'Kids\' Play & Learning Spaces',
         'description': 'Indoor play zones, outdoor adventure trails and a dedicated STEM activity room.'},
        {'icon': '🧘', 'name': 'Wellness Spa & Yoga Pavilion',
         'description': 'Steam, sauna, massage suites and an open-air yoga platform overlooking the greens.'},
        {'icon': '💻', 'name': 'Co-work & Private Meeting Suites',
         'description': 'Sound-proofed pods, video-call booths, collaborative desks and a mini business centre.'},
        {'icon': '🌿', 'name': 'Landscaped Greens & Sit-outs',
         'description': 'Walking trails, bonsai gardens, reflexology paths and a dedicated pet park.'},
        {'icon': '🎭', 'name': 'Mini Theatre & Events Lawn',
         'description': '48-seat private cinema and a 5,000 sq.ft. events lawn for celebrations.'},
        {'icon': '🔒', 'name': 'Multi-tier Security',
         'description': '3-layer access control, CCTV with AI analytics, panic buttons and 24/7 manned gates.'},
    ]
    for order, data in enumerate(amenities, 1):
        CampaignAmenity.objects.create(campaign=campaign, order=order, **data)


def remove_apartment_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    try:
        Campaign.objects.get(slug='prestige-horizon-grand').delete()
    except Campaign.DoesNotExist:
        pass


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0003_extend_campaign_full_landing'),
    ]

    operations = [
        migrations.RunPython(create_apartment_campaign, remove_apartment_campaign),
    ]
