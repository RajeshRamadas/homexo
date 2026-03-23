"""
blog/api_views.py
"""
from rest_framework import viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from .models import Post, Category
from .serializers import PostListSerializer, PostDetailSerializer, CategorySerializer


class PostViewSet(viewsets.ReadOnlyModelViewSet):
    queryset           = Post.objects.filter(status='published').select_related('author').prefetch_related('categories')
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'excerpt', 'body']
    ordering_fields    = ['published_at', 'views_count']
    lookup_field       = 'slug'

    def get_serializer_class(self):
        return PostDetailSerializer if self.action == 'retrieve' else PostListSerializer


class CategoryViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = Category.objects.all()
    serializer_class = CategorySerializer
