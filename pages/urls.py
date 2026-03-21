from django.urls import path
from . import views

app_name = 'pages'

urlpatterns = [
    path('',               views.home,               name='home'),
    path('about/',         views.about,              name='about'),
    path('faq/',           views.faq,                name='faq'),
    path('contact/',       views.contact,            name='contact'),
    path('area-guides/',   views.area_guides,        name='area_guides'),
    path('market-reports/',views.market_reports,     name='market_reports'),
    path('developers/',    views.developers,          name='developers'),
    path('developers/<slug:slug>/', views.developer_profile, name='developer_profile'),
    path('services/security/',        views.security,        name='security'),
    path('services/home-service/',    views.home_service,    name='home_service'),
    path('services/legal/',            views.legal,            name='legal'),
    path('services/legal-homeloan/',  views.legal_homeloan,  name='legal_homeloan'),
    path('services/home-loan/',         views.home_loan,        name='home_loan'),
    path('emi/',             views.emi_calculator,  name='emi_calculator'),
    path('emi/calculate/',   views.emi_calculate_api, name='emi_calculate_api'),
]
