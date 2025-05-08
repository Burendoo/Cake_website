from django.urls import path
from . import views

urlpatterns = [
    path('', views.HomeView.as_view(), name='home'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('contact/', views.contact, name='contact'),
    path('all-cakes/', views.all_cakes, name='all-cakes'),
    path('checkout/<int:cake_id>', views.checkout, name='checkout'),
    path('create-checkout-session/<int:cake_id>', views.create_checkout_session, name='create_checkout_session'),
    path('payment-success', views.payment_success, name='payment_success'),
    path('payment-failed', views.payment_failed, name='payment_failed'),
    path('cake/<slug:cake_slug>', views.SingleCakeView.as_view(), name="cake_info" ),
    path('flavour/<slug:flavour_slug>', views.flavours, name='cake_by_flavour'),
]
