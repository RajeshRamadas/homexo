"""
enquiries/serializers.py
"""
from rest_framework import serializers
from .models import Enquiry


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Enquiry
        fields = ('id', 'name', 'email', 'phone', 'enquiry_type',
                  'budget', 'message', 'property', 'agent', 'created_at')
        read_only_fields = ('id', 'created_at')
