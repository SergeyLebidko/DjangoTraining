from rest_framework.permissions import BasePermission


class MyPermission(BasePermission):

    def has_permission(self, request, view):
        print('Внутри класса-разрешения!', request.user)
        return True
