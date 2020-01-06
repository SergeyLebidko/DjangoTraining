from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count, Max, Min, Avg, Sum, F
from django.views.decorators.http import require_GET
from datetime import date, timedelta
import random

from .models import Order, Client, Product


@require_GET
def index(request):
    context = {
        'hooks': [
            ['GET /create_orders/?count=<Количество создаваемых заказов>', 'Создает в базе новый набор заказов'],
            ['GET /statistic/', 'Возвращает статистику по клиентам/заказам/товарам']
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

    result = {'Создано заказов': str(orders_count)}
    return JsonResponse(result)


@require_GET
def statistic(request):
    result = {}

    # values возвращает queryset, содержащий словари
    # clients = Client.objects.values('title')
    # result['Список клиентов (получен с помощью values)'] = list(clients)

    # values_list возвращает queryset, содержащий кортежи
    # clients = Client.objects.values_list('title')
    # result['Список клиентов (получен с помощью values_list (flat=False))'] = list(clients)

    # values_list с пареметром flat=True возвращает queryset, содержащий значения поля
    clients = Client.objects.values_list('title', flat=True)
    result['Список клиентов (получен с помощью values_list (flat=True))'] = list(clients)

    # Пример использования функции aggregate для получения сводной информации по всей таблице клиентов сразу
    agr_values = Client.objects.aggregate(
        count_clients=Count('title'),
        credit_limit_max=Max('credit_limit'),
        credit_limit_min=Min('credit_limit'),
        credit_limit_avg=Avg('credit_limit'),
        credit_limit_sum=Sum('credit_limit')
    )
    result['Сводные данные по всем клиентам'] = agr_values

    # Получаем информацию о количестве заказов, сделанных каждым клиентом
    clients_with_order_counts = Client.objects.annotate(Count('order')).order_by('-order__count')
    result['Количество заказов, сделанных клиентами'] = {
        client.title: client.order__count for client in clients_with_order_counts
    }

    # По примеру формирования списка клиентов формируем и список товаров
    products = Product.objects.values('title', 'balance', 'price')
    result['Список товаров с остатками и ценами'] = list(products)

    # Суммарная стоимость всех товаров на складе
    product_balance = F('balance')
    product_price = F('price')
    total_cost = Product.objects.aggregate(summary_cost=Sum(product_balance*product_price))
    result['Суммарная стоимость всех товаров на складе'] = total_cost['summary_cost']

    # Количество заказов
    orders_count = Order.objects.count()
    result['Общее количество заказов в базе'] = orders_count

    # Список заказов с суммой каждого заказа (можно ли дать имя вычисляемому полю? спросить у Жени)
    orders_list = Order.objects.values_list(
        'client__title',
        'product__title',
        'dt_create',
        F('count')*F('product__price')
    )
    orders_list = list(orders_list)
    orders_list.sort(reverse=True, key=lambda e: e[3])
    result['Список заказов с суммой каждого заказа'] = orders_list

    return JsonResponse(result)
