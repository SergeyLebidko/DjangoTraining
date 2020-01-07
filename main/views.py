from django.http import JsonResponse
from django.shortcuts import render
from django.db.models import Count, Max, Min, Avg, Sum, F, Prefetch
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
    total_cost = Product.objects.aggregate(summary_cost=Sum(F('balance')*F('price')))
    result['Суммарная стоимость всех товаров на складе'] = total_cost['summary_cost']

    # Количество заказов
    orders_count = Order.objects.count()
    result['Общее количество заказов в базе'] = orders_count

    # Список заказов с суммой каждого заказа (можно ли дать имя вычисляемому полю? спросить у Жени)
    orders_list = Order.objects.values_list(
        'client__title',
        'product__title',
        'dt_create',
        'count',
        F('count')*F('product__price')
    )
    orders_list = list(orders_list)
    orders_list.sort(reverse=True, key=lambda e: e[4])
    result['Список заказов с суммой каждого заказа'] = orders_list

    # Среднее количество товаров в заказе
    avg_count_in_order = Order.objects.aggregate(Avg('count'))['count__avg']
    result['Среднее количество товаров в заказе'] = avg_count_in_order

    # Получаем список клиентов и для каждого подсчитываем сумму сделанных им заказов
    # Клиенты, не сделавшие ни одного заказа - отсекаются (filter(sum_counts__isnull=False))
    # Результаты сортируются по возрастанию суммы заказа
    clients_order_cost = Client.objects.annotate(
        sum_counts=Sum(
            F('order__count')*F('order__product__price')
        )
    ).filter(sum_counts__isnull=False).order_by('sum_counts')
    result['Список клиентов и сумма их заказов'] = [
        {client.title: client.sum_counts} for client in clients_order_cost
    ]

    # Получаем список клиентов, превысивших свой кредитный лимит
    clients_over_limit = Client.objects.annotate(
        sum_counts=Sum(
            F('order__count')*F('order__product__price')
        )
    ).filter(sum_counts__isnull=False, sum_counts__gt=F('credit_limit'))
    result['Список клиентов, превысивших свой кредитный лимит'] = [
        {
            'Клиент': client.title,
            'Превышение лимина': (client.sum_counts-client.credit_limit)
        } for client in clients_over_limit
    ]

    # Получаем товары, которых заказано больше их наличия на складе
    products_over_balance = Product.objects.annotate(
        sum_counts=Sum('order__count')
    ).filter(sum_counts__isnull=False, sum_counts__gt=F('balance'))
    result['Список товаров, которых заказано больше их количества на складе'] = [
        {
            'Товар': product.title,
            'Превышение количества': (product.sum_counts - product.balance)
        } for product in products_over_balance
    ]

    # Пример использования класса Prefetch: выбор всех клиентов, которые заказывали видеокарты
    video_pr = Prefetch(
        'order_set',
        queryset=Order.objects.filter(product__title__istartswith='Видеокарта'),
        to_attr='video_orders'
    )
    clients_videocard = Client.objects.prefetch_related(video_pr).all()
    result['Клиенты, заказавшие видеокарты'] = [
        {
            'Клиент': client.title,
            'Заказы': [
                order.__str__() for order in client.video_orders
            ]
        } for client in clients_videocard if client.video_orders
    ]

    return JsonResponse(result)
