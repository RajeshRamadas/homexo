"""
properties/forms.py
Search and create/edit forms for properties.
"""

from django import forms
from .models import Property


class PropertySearchForm(forms.Form):
    location      = forms.CharField(required=False, widget=forms.TextInput(
                        attrs={'placeholder': 'Search by locality, city...'}))
    listing_type  = forms.ChoiceField(required=False,
                        choices=[('', 'All Types')] + list(Property.ListingType.choices))
    property_type = forms.ChoiceField(required=False,
                        choices=[('', 'All Properties')] + list(Property.PropertyType.choices))
    bhk           = forms.ChoiceField(required=False,
                        choices=[('', 'Any BHK')] + list(Property.BHK.choices))
    price         = forms.ChoiceField(required=False, choices=[
                        ('', 'Any Price'),
                        ('under50l',  'Under ₹50L'),
                        ('50l-1cr',   '₹50L – ₹1Cr'),
                        ('1cr-3cr',   '₹1Cr – ₹3Cr'),
                        ('3cr-10cr',  '₹3Cr – ₹10Cr'),
                        ('above10cr', 'Above ₹10Cr'),
                    ])


class PropertyCreateForm(forms.ModelForm):
    class Meta:
        model  = Property
        fields = (
            'title', 'listing_type', 'property_type', 'description',
            'price', 'price_label', 'price_on_req',
            'bhk', 'bedrooms', 'bathrooms', 'area_sqft', 'carpet_area',
            'address', 'locality', 'city', 'state', 'pincode',
            'floor_no', 'total_floors', 'furnishing', 'facing',
            'age_years', 'parking_slots', 'two_wheeler_parking', 'four_wheeler_parking',
            'construction_status', 'possession_date',
            'ownership_type', 'rera_approved', 'rera_number',
            'title_verified', 'is_negotiable',
            'latitude', 'longitude',
            'tags',
        )
        widgets = {
            'description':     forms.Textarea(attrs={'rows': 5}),
            'address':         forms.Textarea(attrs={'rows': 3}),
            'possession_date': forms.DateInput(attrs={'type': 'date'}),
            'tags':            forms.CheckboxSelectMultiple(),
        }
