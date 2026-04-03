"""
accounts/forms.py
Registration, login, and profile forms.
"""

from django import forms
from django.contrib.auth import authenticate
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import User


class RegisterForm(UserCreationForm):
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    first_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone      = forms.CharField(max_length=20, required=True,
                                 widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    role       = forms.ChoiceField(choices=[
                     ('buyer',  'I want to Buy / Rent'),
                     ('seller', 'I want to List / Sell'),
                 ])

    class Meta:
        model  = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip() or None
        if phone and User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('An account with this phone number already exists.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone')
        if commit:
            user.save()
        return user


class LoginForm(forms.Form):
    email    = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Password'}))

    def clean(self):
        email    = self.cleaned_data.get('email')
        password = self.cleaned_data.get('password')
        if email and password:
            self.user = authenticate(username=email, password=password)
            if not self.user:
                # Give a specific message if the account exists but email is unconfirmed
                if User.objects.filter(email=email, is_active=False, is_verified=False).exists():
                    raise forms.ValidationError(
                        'Please confirm your email address before signing in. '
                        'Check your inbox for the confirmation link.'
                    )
                raise forms.ValidationError('Invalid email or password.')
            if not self.user.is_active:
                raise forms.ValidationError('This account has been deactivated.')
        return self.cleaned_data

    def get_user(self):
        return getattr(self, 'user', None)


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model  = User
        fields = ('first_name', 'last_name', 'phone', 'avatar')
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Phone Number'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip() or None
        if phone and User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This phone number is already linked to another account.')
        return phone


class ProfileCompleteForm(forms.ModelForm):
    """Shown as a popup after social-auth registration for missing info."""

    class Meta:
        model  = User
        fields = (
            'first_name', 'last_name', 'phone',
            'preferred_city', 'preferred_listing_type',
            'preferred_property_type', 'preferred_bhk',
        )
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name':  forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'phone':      forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'preferred_city': forms.TextInput(attrs={'placeholder': 'e.g. Bangalore'}),
            'preferred_listing_type':  forms.Select(choices=[('', 'Select…')] + [
                ('buy', 'Buy'), ('rent', 'Rent'),
                ('new_project', 'New Project'), ('commercial', 'Commercial'),
            ]),
            'preferred_property_type': forms.Select(choices=[('', 'Select…')] + [
                ('apartment', 'Apartment'), ('villa', 'Villa'),
                ('penthouse', 'Penthouse'), ('plot', 'Plot / Land'),
                ('office', 'Office Space'), ('shop', 'Shop / Retail'),
                ('warehouse', 'Warehouse'),
            ]),
            'preferred_bhk': forms.Select(choices=[('', 'Select…')] + [
                ('studio', 'Studio'), ('1bhk', '1 BHK'), ('2bhk', '2 BHK'),
                ('3bhk', '3 BHK'), ('4bhk', '4 BHK'), ('5bhk', '5 BHK'),
                ('6+bhk', '6+ BHK'),
            ]),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip() or None
        if phone and User.objects.filter(phone=phone).exclude(pk=self.instance.pk).exists():
            raise forms.ValidationError('This phone number is already linked to another account.')
        return phone


# Admin forms
class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ('email',)


class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model  = User
        fields = ('email',)


class AdvocateRegisterForm(UserCreationForm):
    email      = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))
    first_name = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name  = forms.CharField(max_length=80, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    phone      = forms.CharField(max_length=20, required=True, widget=forms.TextInput(attrs={'placeholder': 'Phone Number'}))
    bar_number              = forms.CharField(max_length=50, required=True, widget=forms.TextInput(attrs={'placeholder': 'Bar Registration Number'}))
    address                 = forms.CharField(required=True, widget=forms.Textarea(attrs={'placeholder': 'Full Residential/Office Address', 'rows': 3}))
    bar_council_certificate = forms.ImageField(required=True, label='Bar Council Certificate')
    aadhaar_image           = forms.ImageField(required=True, label='Aadhaar Card')
    address_proof_image     = forms.ImageField(required=True, label='Address Proof')

    class Meta:
        model  = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'address', 'bar_number', 'bar_council_certificate', 'aadhaar_image', 'address_proof_image')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email__iexact=email).exists():
            raise forms.ValidationError('An account with this email address already exists.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip() or None
        if phone and User.objects.filter(phone=phone).exists():
            raise forms.ValidationError('An account with this phone number already exists.')
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data.get('phone')
        user.bar_number = self.cleaned_data.get('bar_number')
        user.address = self.cleaned_data.get('address')
        user.bar_council_certificate = self.cleaned_data.get('bar_council_certificate')
        user.aadhaar_image = self.cleaned_data.get('aadhaar_image')
        user.address_proof_image = self.cleaned_data.get('address_proof_image')
        
        user.role = 'advocate'
        user.is_approved_advocate = False
        user.is_active = False # Require email confirmation like standard users; Admin will approve via backend.
        if commit:
            user.save()
        return user
