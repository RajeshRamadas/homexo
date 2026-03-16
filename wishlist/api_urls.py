from django.urls import path
from .api_views import WishlistListAPIView, WishlistToggleAPIView

urlpatterns = [
    path('',                          WishlistListAPIView.as_view(),   name='api-wishlist-list'),
    path('toggle/<int:property_id>/', WishlistToggleAPIView.as_view(), name='api-wishlist-toggle'),
]
