from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET
from datetime import date, timedelta
import random

from .models import Order, Client, Product


@require_GET
def index(request):
    context = {
        'hooks': [
            ['POST create_orders/?count=<Количество создаваемых заказов>', 'Создает в базе новый набор заказов']
        ]
    }
    return render(request, 'main/hooks.html', context)


@require_GET
def create_orders(request):
    # Получаем количество заказаов, которые будем формировать
    orders_count = request.GET.get('orders_count')
    if not orders_count:
        orders_count = request.default_orders_count
    orders_count = int(orders_count)

    # Предварительно очищаем БД от старых заказов
    Order.objects.all().delete()

    # Получаем списки клиентов и товаров
    clients = Client.objects.all()
    products = Product.objects.all()

    # Добавляем новые заказы
    today = date.today()
    for i in range(0, orders_count):
        client = random.choice(clients)
        product = random.choice(products)

        t_delta = timedelta(days=random.randint(0, 10))
        dt_create = today - t_delta

        count = random.randint(1, 10)

        Order.objects.create(
            client=client,
            product=product,
            dt_create=dt_create,
            count=count
        )

    return HttpResponse('Создано заказов: '+str(orders_count))
