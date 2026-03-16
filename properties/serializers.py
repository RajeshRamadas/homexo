"""
properties/serializers.py
DRF serializers for Property, PropertyImage, PropertyFeature, PropertyTag.
"""

from rest_framework import serializers
from .models import Property, PropertyImage, PropertyFeature, PropertyTag


class PropertyTagSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PropertyTag
        fields = ('id', 'name', 'slug')


class PropertyImageSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PropertyImage
        fields = ('id', 'image', 'caption', 'is_primary', 'order')


class PropertyFeatureSerializer(serializers.ModelSerializer):
    class Meta:
        model  = PropertyFeature
        fields = ('id', 'name', 'icon')


class PropertyListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list/cards — minimal fields."""
    display_price = serializers.ReadOnlyField()
    primary_image = serializers.SerializerMethodField()
    location      = serializers.SerializerMethodField()

    class Meta:
        model  = Property
        fields = (
            'id', 'title', 'slug', 'listing_type', 'property_type',
            'display_price', 'price_label', 'price_on_req',
            'bedrooms', 'bathrooms', 'area_sqft', 'bhk',
            'locality', 'city', 'location',
            'is_featured', 'is_signature', 'is_new', 'is_exclusive',
            'primary_image', 'views_count', 'created_at',
        )

    def get_primary_image(self, obj):
        img = obj.primary_image
        if img and img.image:
            request = self.context.get('request')
            return request.build_absolute_uri(img.image.url) if request else img.image.url
        return None

    def get_location(self, obj):
        return f'{obj.locality}, {obj.city}'


class PropertyDetailSerializer(serializers.ModelSerializer):
    """Full serializer for property detail page."""
    display_price = serializers.ReadOnlyField()
    images        = PropertyImageSerializer(many=True, read_only=True)
    features      = PropertyFeatureSerializer(many=True, read_only=True)
    tags          = PropertyTagSerializer(many=True, read_only=True)
    agent         = serializers.SerializerMethodField()

    class Meta:
        model  = Property
        fields = (
            'id', 'title', 'slug', 'description',
            'listing_type', 'property_type', 'bhk',
            'price', 'display_price', 'price_label', 'price_on_req',
            'address', 'locality', 'city', 'state', 'pincode',
            'latitude', 'longitude',
            'bedrooms', 'bathrooms', 'area_sqft', 'carpet_area',
            'floor_no', 'total_floors', 'furnishing', 'facing',
            'age_years', 'parking_slots', 'possession_date',
            'is_featured', 'is_signature', 'is_new', 'is_exclusive',
            'status', 'views_count',
            'images', 'features', 'tags', 'agent',
            'created_at', 'updated_at',
        )

    def get_agent(self, obj):
        if obj.agent:
            return {
                'id':    obj.agent.id,
                'name':  obj.agent.user.get_full_name(),
                'phone': obj.agent.phone,
                'photo': obj.agent.photo.url if obj.agent.photo else None,
            }
        return None


class PropertyCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Property
        exclude = ('owner', 'status', 'views_count', 'slug', 'created_at', 'updated_at')

    def create(self, validated_data):
        tags = validated_data.pop('tags', [])
        prop = Property.objects.create(**validated_data)
        prop.tags.set(tags)
        return prop
