import os
import django
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "homexo.settings")
django.setup()

from properties.models import Property

props = Property.objects.all()
for p in props:
    plans = p.floor_plans.all()
    if len(plans) > 1:
        types = set(fp.bhk_type for fp in plans)
        if len(types) >= 1:
            print(f"URL: /properties/{p.slug}/  (Plans: {len(plans)}, Types: {types})")
