# Посредник нужен для выставления значений по-умолчанию для параметров, которые не были переданы в запросе
def parameters_checker(get_response):
    def core_middleware(request):

        # Выставляем значение по-умолчанию для количества создаваемых заказов
        if request.path == '/create_orders/':
            if 'orders_count' not in request.GET:
                request.default_orders_count = 20

        response = get_response(request)
        return response

    return core_middleware


class MiddleTest:

    def __init__(self, next_middle_func):
        self.next_middle_func = next_middle_func

    def __call__(self, request, *args, **kwargs):
        print('Сработал посредник-класс')
        response = self.next_middle_func(request)
        return response

