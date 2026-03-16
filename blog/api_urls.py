from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import PostViewSet, CategoryViewSet

router = DefaultRouter()
router.register(r'posts',      PostViewSet,     basename='post')
router.register(r'categories', CategoryViewSet, basename='blog-category')

urlpatterns = [path('', include(router.urls))]
