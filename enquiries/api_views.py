"""
enquiries/api_views.py
"""
from rest_framework import generics
from rest_framework.permissions import AllowAny
from .models import Enquiry
from .serializers import EnquirySerializer


class EnquiryCreateAPIView(generics.CreateAPIView):
    """POST /api/v1/enquiries/ — submit an enquiry (public)."""
    queryset           = Enquiry.objects.all()
    serializer_class   = EnquirySerializer
    permission_classes = [AllowAny]

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)
