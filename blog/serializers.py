"""
blog/serializers.py
"""
from rest_framework import serializers
from .models import Post, Category


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model  = Category
        fields = ('id', 'name', 'slug', 'color')


class PostListSerializer(serializers.ModelSerializer):
    category     = CategorySerializer(read_only=True)
    author_name  = serializers.SerializerMethodField()
    cover_image  = serializers.SerializerMethodField()

    class Meta:
        model  = Post
        fields = ('id', 'title', 'slug', 'excerpt', 'cover_image',
                  'category', 'author_name', 'published_at', 'views_count')

    def get_author_name(self, obj):
        return obj.author.get_full_name() if obj.author else 'HOMEXO Team'

    def get_cover_image(self, obj):
        if obj.cover_image:
            req = self.context.get('request')
            return req.build_absolute_uri(obj.cover_image.url) if req else obj.cover_image.url
        return None


class PostDetailSerializer(PostListSerializer):
    class Meta(PostListSerializer.Meta):
        fields = PostListSerializer.Meta.fields + ('body', 'created_at', 'updated_at')
