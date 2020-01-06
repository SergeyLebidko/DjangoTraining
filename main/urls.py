from django.urls import path
from .views import index, create_orders, statistic

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('statistic/', statistic, name='statistic'),
    path('', index, name='index')
]
