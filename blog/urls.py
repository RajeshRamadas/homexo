from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    path('',                    views.post_list,   name='list'),
    path('category/<slug:category_slug>/', views.post_list, name='category_list'),
    path('create/',             views.post_create, name='create'),
    path('<slug:slug>/edit/',   views.post_edit,   name='edit'),
    path('<slug:slug>/',        views.post_detail, name='detail'),
]
