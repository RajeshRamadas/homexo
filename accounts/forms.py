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
    phone      = forms.CharField(max_length=20, required=False,
                                 widget=forms.TextInput(attrs={'placeholder': 'Phone Number (optional)'}))
    role       = forms.ChoiceField(choices=[
                     ('buyer',  'I want to Buy / Rent'),
                     ('seller', 'I want to List / Sell'),
                 ])

    class Meta:
        model  = User
        fields = ('email', 'first_name', 'last_name', 'phone', 'role', 'password1', 'password2')

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
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


# Admin forms
class AdminUserCreationForm(UserCreationForm):
    class Meta:
        model  = User
        fields = ('email',)


class AdminUserChangeForm(UserChangeForm):
    class Meta:
        model  = User
        fields = ('email',)
