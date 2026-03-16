"""
wishlist/serializers.py
"""
from rest_framework import serializers
from properties.serializers import PropertyListSerializer
from .models import WishlistItem


class WishlistItemSerializer(serializers.ModelSerializer):
    property = PropertyListSerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        queryset=__import__('properties.models', fromlist=['Property']).Property.objects.all(),
        source='property', write_only=True
    )

    class Meta:
        model  = WishlistItem
        fields = ('id', 'property', 'property_id', 'created_at')
        read_only_fields = ('id', 'created_at')
