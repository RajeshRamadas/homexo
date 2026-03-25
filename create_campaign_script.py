import os
import django
from django.core.files import File

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'homexo.settings')
django.setup()

from campaigns.models import Campaign, CampaignHighlight, CampaignFloorPlan, CampaignAmenity, CampaignGalleryImage

# define the paths
hero_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/hero_building_1774465369405.png'
about_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/about_lobby_1774465399914.png'
pool_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/amenity_pool_1774465422183.png'
gym_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/amenity_gym_1774465445635.png'
highlight_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/highlight_view_1774465491943.png'
living_img = '/home/rajesh/.gemini/antigravity/brain/e4de54b6-7dfc-42aa-a48a-48d3ca320e6a/gallery_living_1774465509028.png'

print("Creating Premium Campaign...")

camp = Campaign.objects.create(
    title='The Ascent Residences',
    developer_name='Astra Developers',
    accent_color='#D4AF37',  # Gold accent
    popup_bg_color='#1A1A1A',
    nav_style='branded',
    nav_cta_text='Schedule Private Viewing',
    hero_heading='Elevate Your Lifestyle|The Ascent Residences',
    hero_sub='Discover ultra-luxury living with panoramic city views and exclusive, world-class amenities.',
    stat_land_parcel='5 Acres',
    stat_floors='G + 45',
    stat_configs='3, 4 & 5 BHK',
    stat_possession='Dec 2028',
    stat_price_start='₹4.5 Crore Onwards*',
    offer_label='Launch Offer: Priority Allotment',
    about_heading='Redefining Skyline Luxury',
    about_body='The Ascent is not just a residence; it is a statement of prestige. Crafted with meticulous attention to detail, every home offers unmatched grandeur, expansive spaces, and a lifestyle reserved for the select few.',
    masterplan_heading='Architectural Brilliance',
    masterplan_body='Thoughtfully designed layout prioritizing open spaces, privacy, and seamless connectivity to luxury amenities.',
    location_heading='The Pinnacle of Connectivity',
    location_body='Situated in the heart of the city\'s most coveted neighborhood, offering seamless elite living with premium malls, top-tier schools, and corporate hubs just minutes away.',
    cta_heading='Your Luxury Awaits',
    cta_sub='Register now for priority access to the finest residences.',
    cta_button_text='Request Details',
    footer_style='branded',
    footer_tagline='Crafting Legacies in Luxury',
    footer_email='sales@astradevelopers.com',
    footer_phone='+91 98765 00000',
    contact_phone='+919876500000'
)

with open(hero_img, 'rb') as f:
    camp.hero_bg.save('ascent_hero.png', File(f), save=True)

with open(about_img, 'rb') as f:
    camp.about_image.save('ascent_about.png', File(f), save=True)

# Amenities
a1 = CampaignAmenity.objects.create(campaign=camp, name='Infinity Pool', description='Stunning temperature-controlled infinity pool offering panoramic skyline views.', order=1)
with open(pool_img, 'rb') as f:
    a1.image.save('pool.png', File(f), save=True)

a2 = CampaignAmenity.objects.create(campaign=camp, name='State-of-the-Art Gym', description='Fully equipped premium fitness center with expert trainers available.', order=2)
with open(gym_img, 'rb') as f:
    a2.image.save('gym.png', File(f), save=True)

a3 = CampaignAmenity.objects.create(campaign=camp, name='Private Theater', description='Exclusive resident-only cinematic experience.', order=3)

# Highlights
h1 = CampaignHighlight.objects.create(campaign=camp, heading='Panoramic Views', body='Uninterrupted views of the city skyline and lush green landscapes from every residence.', order=1)
with open(highlight_img, 'rb') as f:
    h1.image.save('views.png', File(f), save=True)

h2 = CampaignHighlight.objects.create(campaign=camp, heading='Smart Home Integration', body='Next-generation automation for lighting, climate control, and security.', order=2)
h3 = CampaignHighlight.objects.create(campaign=camp, heading='Elite Concierge', body='24/7 dedicated concierge service catering to your every lifestyle need.', order=3)

# Floor Plans
CampaignFloorPlan.objects.create(campaign=camp, config='3 BHK Premium', sba_range='2,800 - 3,100 sq.ft.', price_range='₹4.5 - 5.2 Cr*', order=1)
CampaignFloorPlan.objects.create(campaign=camp, config='4 BHK Luxury', sba_range='3,800 - 4,200 sq.ft.', price_range='₹6.8 - 7.5 Cr*', order=2)
CampaignFloorPlan.objects.create(campaign=camp, config='5 BHK Penthouse', sba_range='6,500 sq.ft.', price_range='₹12.5 Cr*', order=3)

# Gallery
g1 = CampaignGalleryImage.objects.create(campaign=camp, caption='Luxury Living Room', order=1)
with open(living_img, 'rb') as f:
    g1.image.save('living.png', File(f), save=True)

print(f"Campaign '{camp.title}' created successfully at /{camp.slug}/")
