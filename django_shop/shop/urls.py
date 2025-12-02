from django.urls import path

from . import views

app_name = 'shop'

urlpatterns = [
    path('', views.product_list, name='product_list'),
    path('buy/<slug:slug>/', views.buy_product, name='buy_product'),
]
