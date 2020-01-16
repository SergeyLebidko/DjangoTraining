from django.urls import path
from .views import index, create_orders, statistic, spec_stat, test_response

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('statistic/', statistic, name='statistic'),
    path('spec_stat/<str:stat_type>/', spec_stat, name='spec_stat'),
    path('test_response/', test_response, name='test_response'),
    path('', index, name='index')
]
