from django.http import JsonResponse

from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, RetrieveModelMixin, CreateModelMixin

from django.shortcuts import render
from django.db.models import Count, Max, Min, Avg, Sum, F, Q, Prefetch
from django.views.decorators.http import require_GET
from datetime import date, timedelta
import random

from .models import Order, Client, Product
from .serializers import SimpleClientSerializer, ClientSerializer, PersonSerializer, ProductSerializer
from .addition import Person


@require_GET
def index(request):
    context = {
        'hooks': [
            ['GET /create_orders/?count=<Количество создаваемых заказов>', 'Создает в базе новый набор заказов'],
            ['GET /statistic/', 'Возвращает статистику по клиентам/заказам/товарам'],
            ['GET /spec_stat/sum_limits/', 'Возвращает сумму кредитных лимитов всех клиентов'],
            ['GET /spec_stat/sum_limits_vip/', 'Возвращает сумму кредитных лимитов vip-клиентов'],
            ['GET /spec_stat/limit_over_avg/', 'Возвращает всех клиентов, у которых кредитный лимит выше среднего'],
            ['GET /spec_stat/clients_and_orders/', 'Клиенты и список их заказов'],
            ['GET /spec_stat/vip_clients_and_orders_video/', 'vip-клиенты и список их заказов, включающих видеокарты'],
            ['GET /spec_stat/products_cost/', 'Список товаров с их полной стоимостью (цена*количество)'],
            ['GET /get_clients/', 'Список клиентов (формируется с помощью DRF)'],
            ['GET /create_client/', 'Создать клиента (формируется с помощью DRF)'],
            ['GET /test/', 'Хук для тестовых запросов'],
            ['GET или POST /person_demo/', 'Хук для тестирования работы с сериализатором обычного объекта'],
            ['GET /get_detailed_clients/', 'Выводит список клиентов, свомещенный со списками id их заказов'],
            ['GET /get_url_list/', 'Выводит список всех элементов списка urlpatterns'],
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


@require_GET
def spec_stat(request, stat_type):
    # Получаем сумму всех кретидных лимитов клиентов
    if stat_type == 'sum_limits':
        sum_limits = Client.objects.aggregate(sum=Sum('credit_limit'))['sum']
        result = {'Сумма кредитных лимитов клиентов': sum_limits}

    # Получаем сумму кредитных лимитов всех клиентов
    if stat_type == 'sum_limits_vip':
        sum_limits_vip = Client.objects.aggregate(
            sum=Sum('credit_limit', filter=Q(vip=True))
        )['sum']
        result = {'Сумма кредитных лимитов VIP-клиентов': sum_limits_vip}

    # Получаем всех клиентов, у которых кредитный лимит выше среднего
    if stat_type == 'limit_over_avg':
        avg_limit = Client.objects.aggregate(avg=Avg('credit_limit'))['avg']
        clients = Client.objects.filter(
            credit_limit__gt=avg_limit
        ).values_list(
            'title', flat=True
        )
        result = {'Клиенты, у которых кредитный лимит выше среднего': list(clients)}

    # Клиенты и список их заказов
    if stat_type == 'clients_and_orders':
        clients = Client.objects.prefetch_related('order_set').all()

        result = {}
        for client in clients:
            result[client.title] = list(client.order_set.all().values('product__title', 'count'))

    # vip-клиенты и список их заказов, включающих видеокарты
    if stat_type == 'vip_clients_and_orders_video':
        pr = Prefetch('order_set', queryset=Order.objects.filter(product__title__contains='Видеокарта'))
        clients = Client.objects.prefetch_related(pr).filter(vip=True)
        result = {}
        for client in clients:
            order_list = list(client.order_set.values_list('product__title', 'count'))
            if order_list:
                result[client.title] = order_list

    # Полная стоимость каждого товара на складе
    if stat_type == 'products_cost':
        products_with_coast = Product.objects.annotate(coast=F('price')*F('balance'))
        result = {'Список товаров': [
            {
                'Товар': p.title,
                'Полная строимость (цена*остаток)': p.coast
            } for p in products_with_coast
        ]}
        print(result)

    return JsonResponse(result)


@api_view(['GET'])
def get_clients(request):
    clients = Client.objects.all()
    serializer = SimpleClientSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def create_client(request):
    serializer = SimpleClientSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response('Запрос принят и успешно обработан')
    else:
        return Response(serializer.errors)


@api_view(['GET'])
def get_detailed_clients(request):
    clients = Client.objects.all()
    serializer = ClientSerializer(clients, many=True)
    return Response(serializer.data)


@api_view(['GET', 'POST'])
def person_demo(request):
    if request.method == 'GET':
        person = Person('Сергей Лебидко', 'm', 35, 'sergeyler@mail.ru')
        serializer = PersonSerializer(person)
        return Response([serializer.data])

    if request.method == 'POST':

        person_for_update = Person(name='Вася Пупкин', gender='m', age=15, email='zadrott@gmail.com')
        original_data = str(person_for_update)

        serializer = PersonSerializer(data=request.data, instance=person_for_update)
        if serializer.is_valid():
            return Response({
                'Данные до обновления экземпляра': original_data,
                'Валидированные данные': serializer.validated_data,
                'Данные после обновления экземпляра': str(serializer.save())
            })
        else:
            return Response(serializer.errors)


@api_view(['GET'])
def get_urls_list(request):
    from .urls import urlpatterns
    return Response([str(url) for url in urlpatterns])


class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer


class ClientViewSet(GenericViewSet, ListModelMixin, RetrieveModelMixin, CreateModelMixin):
    queryset = Client.objects.all()
    serializer_class = SimpleClientSerializer


# Контроллер для быстрого тестирования различных фишек django / drf
# @api_view(['GET'])
def test(request):
    from django.http import HttpResponse
    return HttpResponse(request.GET['dt'])
