from django.urls import path
from .views import index, create_orders, statistic, spec_stat, get_clients, create_client, test

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('statistic/', statistic, name='statistic'),
    path('spec_stat/<str:stat_type>/', spec_stat, name='spec_stat'),
    path('get_clients/', get_clients, name='get_clients'),
    path('create_client/', create_client, name='create_client'),
    path('test/', test, name='test'),
    path('', index, name='index')
]
