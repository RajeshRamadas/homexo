from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    path('',         views.enquiry_create,  name='create'),
    path('success/', views.enquiry_success, name='success'),
]
