from django.db import migrations


def create_villa_plot_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    CampaignHighlight = apps.get_model('campaigns', 'CampaignHighlight')

    defaults = {
        'title': 'Premium Villa Plot Sale',
        'developer_name': 'Astra Estates',
        'hero_heading': 'Secure Your Address|Amidst Lush Nature',
        'hero_sub': 'Gated plots starting at 2400 sq.ft with clubhouse-ready infrastructure and RERA approval.',
        'accent_color': '#1F8A70',
        'nav_style': 'cobranded',
        'nav_cta_text': 'Schedule a Site Visit',
        'offer_label': 'Launch Offer · Pay 10% now',
        'about_heading': 'Where resort living meets freehold ownership',
        'about_body': (
            'Spread across 80 acres near Sarjapur, this low-density enclave offers tree-lined avenues, '
            'a 30,000 sq.ft. clubhouse, organic farming patches, and ready infrastructure so you can '
            'design and build your signature villa at your pace.'
        ),
        'cta_heading': 'Claim a Founder’s Advantage',
        'cta_sub': 'Prices from ₹1.2 Cr onwards with easy construction-linked plans and concierge support.',
        'cta_button_text': 'Download Master Layout',
        'footer_style': 'branded',
        'footer_tagline': 'Astra Estates · Villa Plot Collection',
        'footer_address': 'HOMEXO Experience Studio, 5th Floor, Indiranagar, Bengaluru',
        'footer_email': 'plots@homexo.com',
    }

    campaign, created = Campaign.objects.get_or_create(
        slug='villa-plot-sale',
        defaults=defaults,
    )

    if not created:
        for field, value in defaults.items():
            setattr(campaign, field, value)
        campaign.save(update_fields=list(defaults.keys()))

    campaign.highlights.all().delete()
    highlight_data = [
        {'icon': '✓', 'heading': 'Phase 1 infrastructure delivered', 'body': 'Internal roads, power, water and fibre laid with OC expected in Q3.'},
        {'icon': '✓', 'heading': 'Clubhouse and wellness focus', 'body': 'Resort-grade clubhouse with pool, spa suites, sky deck gym and co-work lounge.'},
        {'icon': '✓', 'heading': 'Location that balances calm & access', 'body': '15 mins from Sarjapur ORR, close to upcoming Metro Phase 3 and IT hubs.'},
    ]

    for order, data in enumerate(highlight_data, start=1):
        CampaignHighlight.objects.create(campaign=campaign, order=order, **data)


def remove_villa_plot_campaign(apps, schema_editor):
    Campaign = apps.get_model('campaigns', 'Campaign')
    try:
        campaign = Campaign.objects.get(slug='villa-plot-sale')
    except Campaign.DoesNotExist:
        return
    campaign.delete()


class Migration(migrations.Migration):

    dependencies = [
        ('campaigns', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_villa_plot_campaign, remove_villa_plot_campaign),
    ]
