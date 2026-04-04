from django.urls import path
from . import views

app_name = 'enquiries'

urlpatterns = [
    path('',                      views.enquiry_create,        name='create'),
    path('success/',              views.enquiry_success,        name='success'),
    path('dashboard/',            views.enquiry_dashboard,      name='dashboard'),
    path('bulk/',                 views.enquiry_bulk_action,    name='bulk_action'),
    path('<int:pk>/',             views.enquiry_detail_view,    name='detail'),
    path('<int:pk>/update/',      views.enquiry_update_status,  name='update_status'),
    path('<int:pk>/comment/',     views.enquiry_add_comment,    name='add_comment'),
]
