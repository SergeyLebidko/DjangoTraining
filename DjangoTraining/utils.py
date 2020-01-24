from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)
    if response is not None:
        if isinstance(response.data, dict):
            error = response.data.get('error', '')
            detail = response.data.get('detail', '')
            response.data = f'{error} {detail}'.strip()
    return response
