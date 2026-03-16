from django.urls import path
from . import views

app_name = 'wishlist'

urlpatterns = [
    path('',                          views.wishlist_list,   name='list'),
    path('toggle/<int:property_id>/', views.wishlist_toggle, name='toggle'),
    path('remove/<int:item_id>/',     views.wishlist_remove, name='remove'),
]
