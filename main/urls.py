from django.urls import path
from rest_framework.routers import SimpleRouter

from .views import index, create_orders, statistic, spec_stat, get_clients, get_detailed_clients, \
    create_client, test, person_demo, get_urls_list, ProductViewSet, ClientViewSet, Login, show_current_user, Logout, \
    test_permission

urlpatterns = [
    path('create_orders/', create_orders, name='create_orders'),
    path('statistic/', statistic, name='statistic'),
    path('spec_stat/<str:stat_type>/', spec_stat, name='spec_stat'),
    path('get_clients/', get_clients, name='get_clients'),
    path('create_client/', create_client, name='create_client'),
    path('test/', test, name='test'),
    path('person_demo/', person_demo, name='person_demo'),
    path('get_detailed_clients/', get_detailed_clients, name='get_detailed_clients'),
    path('get_url_list/', get_urls_list, name='get_url_list'),

    path('login/', Login.as_view(), name='login'),
    path('show_current_user/', show_current_user, name='show_current_user'),
    path('logout/', Logout.as_view(), name='logout'),
    path('test_permission/', test_permission, name='test_permission'),

    path('', index, name='index')
]

router = SimpleRouter()
router.register('products', ProductViewSet)
router.register('clients', ClientViewSet)

urlpatterns.extend(router.urls)
