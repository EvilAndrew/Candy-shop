from django.contrib import admin
from django.urls import path
from candy_shop import views

app_name = 'candy_shop'

urlpatterns = [
    path('couriers', views.load_couriers, name='load_couriers'),
    path('couriers/<int:need_id>', views.process_couriers, name='process_couriers'),
    path('orders', views.load_orders, name='load_orders'),
    path('orders/assign', views.assign_orders, name='assign_orders'),
    path('orders/complete', views.complete_order, name='complete_order')
]
