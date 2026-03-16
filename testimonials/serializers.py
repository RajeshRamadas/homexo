"""
testimonials/serializers.py
"""
from rest_framework import serializers
from .models import Testimonial


class TestimonialSerializer(serializers.ModelSerializer):
    avatar_url = serializers.SerializerMethodField()

    class Meta:
        model  = Testimonial
        fields = ('id', 'client_name', 'client_location', 'avatar_url',
                  'rating', 'review', 'created_at')

    def get_avatar_url(self, obj):
        if obj.avatar:
            req = self.context.get('request')
            return req.build_absolute_uri(obj.avatar.url) if req else obj.avatar.url
        return None
