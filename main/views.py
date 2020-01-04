from django.http import HttpResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST, require_GET
from django.views.decorators.csrf import csrf_exempt


@require_GET
def index(request):
    context = {
        'hooks': [
            ['POST create_orders/?count=<Количество создаваемых заказов>', 'Создает в базе новый набор заказов']
        ]
    }
    return render(request, 'main/hooks.html', context)


@csrf_exempt
@require_POST
def create_orders(request):
    count = request.GET['count']
    return HttpResponse('Количество созданных заказов: '+str(count))
