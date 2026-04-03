"""
properties/api_views.py
DRF ViewSets for Property API.
"""

from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from django.db.models import Q

from .models import Property, PropertyTag
from .serializers import (
    PropertyListSerializer, PropertyDetailSerializer,
    PropertyCreateSerializer, PropertyTagSerializer,
)


class PropertyViewSet(viewsets.ModelViewSet):
    """
    GET    /api/v1/properties/          → list  (public)
    POST   /api/v1/properties/          → create (auth)
    GET    /api/v1/properties/<slug>/   → detail (public)
    PUT    /api/v1/properties/<slug>/   → update (owner)
    DELETE /api/v1/properties/<slug>/   → delete (owner)
    GET    /api/v1/properties/featured/ → featured list
    GET    /api/v1/properties/signature/→ signature list
    """
    queryset           = Property.objects.filter(status='active')
    permission_classes = [IsAuthenticatedOrReadOnly]
    lookup_field       = 'slug'
    filter_backends    = [filters.SearchFilter, filters.OrderingFilter]
    search_fields      = ['title', 'locality', 'city', 'description']
    ordering_fields    = ['price', 'created_at', 'views_count', 'area_sqft']
    ordering           = ['-is_featured', '-created_at']

    def get_serializer_class(self):
        if self.action == 'list':
            return PropertyListSerializer
        if self.action == 'create':
            return PropertyCreateSerializer
        return PropertyDetailSerializer

    def get_queryset(self):
        qs = super().get_queryset().select_related('developer').prefetch_related('images', 'tags')

        # Filter params
        listing_type  = self.request.query_params.get('type')
        property_type = self.request.query_params.get('property_type')
        city          = self.request.query_params.get('city')
        bhk           = self.request.query_params.get('bhk')
        min_price     = self.request.query_params.get('min_price')
        max_price     = self.request.query_params.get('max_price')
        bedrooms      = self.request.query_params.get('bedrooms')

        if listing_type:
            qs = qs.filter(listing_type=listing_type)
        if property_type:
            qs = qs.filter(property_type=property_type)
        if city:
            qs = qs.filter(city__icontains=city)
        if bhk:
            qs = qs.filter(bhk=bhk)
        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)
        if bedrooms:
            qs = qs.filter(bedrooms=bedrooms)

        return qs

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user, status='pending')

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.increment_views()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def featured(self, request):
        qs = self.get_queryset().filter(is_featured=True)[:6]
        return Response(PropertyListSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def signature(self, request):
        qs = self.get_queryset().filter(is_signature=True)
        return Response(PropertyListSerializer(qs, many=True, context={'request': request}).data)

    @action(detail=False, methods=['get'])
    def my_listings(self, request):
        if not request.user.is_authenticated:
            return Response({'detail': 'Authentication required.'}, status=status.HTTP_401_UNAUTHORIZED)
        qs = Property.objects.filter(owner=request.user)
        return Response(PropertyListSerializer(qs, many=True, context={'request': request}).data)


class PropertyTagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset         = PropertyTag.objects.all()
    serializer_class = PropertyTagSerializer
