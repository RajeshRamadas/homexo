from django.urls import path
from . import views

app_name = 'properties'

urlpatterns = [
    path('',                          views.property_list,        name='list'),
    path('create/',                   views.property_create,      name='create'),
    path('approvals/',                views.approval_dashboard,   name='approval_dashboard'),
    path('approvals/<int:prop_id>/action/', views.approval_action, name='approval_action'),
    path('<slug:slug>/',              views.property_detail,      name='detail'),
    path('<slug:slug>/edit/',         views.property_update,      name='update'),
    path('<slug:slug>/delete/',       views.property_delete,      name='delete'),
    path('featured/json/',            views.featured_properties,  name='featured_json'),
    path('<slug:slug>/report/',       views.report_property,      name='report'),
    path('<int:property_id>/group-buy/', views.group_buy_toggle,  name='group_buy_toggle'),
]
