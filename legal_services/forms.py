from django import forms
from .models import LegalOrder
from django.contrib.auth import get_user_model

User = get_user_model()

class LegalOrderRequestForm(forms.ModelForm):
    advocate = forms.ModelChoiceField(
        queryset=User.objects.filter(role='advocate', is_approved_advocate=True, is_active=True),
        required=False,
        empty_label="Any Available Advocate (Fastest)",
        widget=forms.Select(attrs={'class': 'form-control'})
    )

    class Meta:
        model = LegalOrder
        fields = ['property_name', 'property_address', 'package', 'advocate']
        widgets = {
            'property_name': forms.TextInput(attrs={'placeholder': 'e.g. 3BHK Apartment, Brigade Gateway', 'class': 'form-control'}),
            'property_address': forms.Textarea(attrs={'placeholder': 'Full address of the property to be verified...', 'rows': 3, 'class': 'form-control'}),
            'package': forms.Select(attrs={'class': 'form-control'})
        }
