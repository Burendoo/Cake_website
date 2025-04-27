from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('cake/<slug:cake_slug>', views.SingleCakeView.as_view(), name="cake_info" ),
    path('flavour/<slug:flavour_slug>', views.flavours, name='cake_by_flavour'),
]
