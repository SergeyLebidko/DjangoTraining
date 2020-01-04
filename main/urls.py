from django.urls import path
from .views import index, create_orders

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('', index, name='index')
]
