from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET


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
    count = request.GET.get('count')
    if not count:
        count = request.default_order_count
    return HttpResponse('Количество созданных заказов: '+str(count))
