"""
wishlist/api_views.py
"""
from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from properties.models import Property
from .models import WishlistItem
from .serializers import WishlistItemSerializer


class WishlistListAPIView(generics.ListAPIView):
    """GET /api/v1/wishlist/ — list saved properties."""
    serializer_class   = WishlistItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return WishlistItem.objects.filter(user=self.request.user).select_related('property')


class WishlistToggleAPIView(APIView):
    """POST /api/v1/wishlist/toggle/<property_id>/ — add or remove."""
    permission_classes = [IsAuthenticated]

    def post(self, request, property_id):
        prop = generics.get_object_or_404(Property, pk=property_id)
        item, created = WishlistItem.objects.get_or_create(
            user=request.user, property=prop
        )
        if not created:
            item.delete()
            return Response({'saved': False}, status=status.HTTP_200_OK)
        return Response({'saved': True}, status=status.HTTP_201_CREATED)
