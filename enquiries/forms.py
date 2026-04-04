"""
enquiries/forms.py
"""
from django import forms
from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    # Email is optional — phone is the primary contact; several CTA forms don't ask for it
    email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}),
    )

    class Meta:
        model  = Enquiry
        fields = ('name', 'email', 'phone', 'enquiry_type', 'budget', 'message')
        widgets = {
            'name':    forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'phone':   forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'budget':  forms.TextInput(attrs={'placeholder': 'e.g. ₹50L – ₹1Cr'}),
            'message': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your message...'}),
        }
