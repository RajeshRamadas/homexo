from django.urls import path
from .api_views import RegisterAPIView, LoginAPIView, LogoutAPIView, MeAPIView

urlpatterns = [
    path('register/', RegisterAPIView.as_view(), name='api-register'),
    path('login/',    LoginAPIView.as_view(),    name='api-login'),
    path('logout/',   LogoutAPIView.as_view(),   name='api-logout'),
    path('me/',       MeAPIView.as_view(),        name='api-me'),
]
