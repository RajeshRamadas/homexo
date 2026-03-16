from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PropertyViewSet, PropertyTagViewSet

router = DefaultRouter()
router.register(r'', PropertyViewSet, basename='property')
router.register(r'tags', PropertyTagViewSet, basename='property-tag')

urlpatterns = [
    path('', include(router.urls)),
]
