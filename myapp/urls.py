from django.urls import path
from .views import DexPricesView, DexTokenOverviewView, BirdPricesView, BirdTokenOverviewView

urlpatterns = [
    path('dex/prices/', DexPricesView.as_view(), name='dex_prices'),
    path('dex/overview/<str:address>/', DexTokenOverviewView.as_view(), name='dex_overview'),
    path('bird/prices/', BirdPricesView.as_view(), name='bird_prices'),
    path('bird/overview/<str:address>/', BirdTokenOverviewView.as_view(), name='bird_overview'),
]
