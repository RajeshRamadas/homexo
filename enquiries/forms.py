"""
enquiries/forms.py
"""
from django import forms
from .models import Enquiry


class EnquiryForm(forms.ModelForm):
    class Meta:
        model  = Enquiry
        fields = ('name', 'email', 'phone', 'enquiry_type', 'budget', 'message')
        widgets = {
            'name':         forms.TextInput(attrs={'placeholder': 'Your Full Name'}),
            'email':        forms.EmailInput(attrs={'placeholder': 'Email Address'}),
            'phone':        forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'budget':       forms.TextInput(attrs={'placeholder': 'e.g. ₹50L – ₹1Cr'}),
            'message':      forms.Textarea(attrs={'rows': 4, 'placeholder': 'Your message...'}),
        }
