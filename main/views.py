from django.http import HttpResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt


@csrf_exempt
@require_POST
def create_orders(request):
    count = request.GET['count']
    return HttpResponse('Количество созданных заказов: '+str(count))
