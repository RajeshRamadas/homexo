from django.urls import path
from .api_views import EnquiryCreateAPIView

urlpatterns = [
    path('', EnquiryCreateAPIView.as_view(), name='api-enquiry-create'),
]
