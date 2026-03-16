"""
agents/serializers.py
"""
from rest_framework import serializers
from .models import Agent


class AgentSerializer(serializers.ModelSerializer):
    full_name      = serializers.ReadOnlyField()
    email          = serializers.ReadOnlyField()
    listings_count = serializers.ReadOnlyField()
    photo_url      = serializers.SerializerMethodField()

    class Meta:
        model  = Agent
        fields = ('id', 'full_name', 'email', 'phone', 'whatsapp', 'photo_url',
                  'bio', 'specialization', 'languages', 'experience_years',
                  'rera_number', 'is_verified', 'rating', 'total_reviews',
                  'listings_count')

    def get_photo_url(self, obj):
        if obj.photo:
            req = self.context.get('request')
            return req.build_absolute_uri(obj.photo.url) if req else obj.photo.url
        return None
