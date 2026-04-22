from django.urls import path
from . import views

app_name = 'legal_services'

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('orders/<uuid:uuid>/', views.order_detail, name='order_detail'),
    path('requests/new/', views.request_order, name='request_order'),
    
    # Advocate Portal
    path('advocates/dashboard/', views.advocate_dashboard, name='advocate_dashboard'),
    path('advocates/pool/', views.advocate_pool, name='advocate_pool'),
    path('advocates/claims/<uuid:uuid>/', views.advocate_claim, name='advocate_claim'),
    path('advocates/orders/<uuid:uuid>/', views.advocate_order_detail, name='advocate_order_detail'),
    
    # Admin Portal
    path('admin-dashboard/', views.admin_legal_dashboard, name='admin_dashboard'),
]
