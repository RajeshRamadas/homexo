"""
accounts/models.py
Custom User model extending AbstractBaseUser.
"""

from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.db import models
from django.utils import timezone
import datetime


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        return self.create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    """
    Custom user model. Email is the primary identifier.
    Roles: buyer, seller, agent, admin.
    """

    class Role(models.TextChoices):
        BUYER            = 'buyer',            'Buyer'
        SELLER           = 'seller',           'Seller'
        AGENT            = 'agent',            'Agent'
        ADMIN            = 'admin',            'Admin'
        LEGAL_ADMIN      = 'legal_admin',      'Legal Admin'
        ADVOCATE         = 'advocate',         'Advocate'
        CUSTOMER_SUPPORT = 'customer_support', 'Customer Support'

    email        = models.EmailField(unique=True, db_index=True)
    first_name   = models.CharField(max_length=80)
    last_name    = models.CharField(max_length=80)
    phone        = models.CharField(max_length=20, blank=True, null=True, unique=True, db_index=True)
    role         = models.CharField(max_length=20, choices=Role.choices, default=Role.BUYER)
    avatar       = models.ImageField(upload_to='avatars/', blank=True, null=True)
    is_verified  = models.BooleanField(default=False)
    is_active    = models.BooleanField(default=True)
    is_staff     = models.BooleanField(default=False)
    date_joined  = models.DateTimeField(default=timezone.now)

    # Profile-completion tracking (False for new social-auth users)
    profile_complete = models.BooleanField(default=True)

    # Property preferences
    preferred_city          = models.CharField(max_length=100, blank=True)
    preferred_listing_type  = models.CharField(max_length=20, blank=True)
    preferred_property_type = models.CharField(max_length=20, blank=True)
    preferred_bhk           = models.CharField(max_length=10, blank=True)
    
    # Advocate specific
    address                 = models.TextField(blank=True, null=True)
    bar_number              = models.CharField(max_length=50, blank=True)
    bar_council_certificate = models.ImageField(upload_to='advocate_docs/bar/', blank=True, null=True)
    aadhaar_image           = models.ImageField(upload_to='advocate_docs/aadhaar/', blank=True, null=True)
    address_proof_image     = models.ImageField(upload_to='advocate_docs/address/', blank=True, null=True)
    is_approved_advocate    = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD  = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        verbose_name        = 'User'
        verbose_name_plural = 'Users'
        ordering            = ['-date_joined']

    def __str__(self):
        return f'{self.get_full_name()} <{self.email}>'

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'.strip()

    def get_short_name(self):
        return self.first_name

    @property
    def is_agent(self):
        return self.role == self.Role.AGENT

    @property
    def is_seller(self):
        return self.role in (self.Role.SELLER, self.Role.AGENT)


class PhoneOTP(models.Model):
    """One-time password for phone-based login. Valid for 10 minutes, single use."""
    phone      = models.CharField(max_length=20, db_index=True)
    otp        = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used    = models.BooleanField(default=False)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'OTP for {self.phone}'

    @property
    def is_valid(self):
        return (
            not self.is_used and
            timezone.now() < self.created_at + datetime.timedelta(minutes=10)
        )
