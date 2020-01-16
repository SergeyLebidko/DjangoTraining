from django.urls import path
from .views import index, create_orders, statistic, spec_stat

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('statistic/', statistic, name='statistic'),
    path('spec_stat/<str:stat_type>/', spec_stat, name='spec_stat'),
    path('', index, name='index')
]
