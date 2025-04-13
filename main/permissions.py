from rest_framework import permissions


class IsAdminOrActiveEmployee(permissions.BasePermission):

    message = "У вас нет доступа к этому ресурсу"

    def has_permission(self, request, view):
        # Проверка аутентификации через токен, если пользователь не аутентифицирован
        if not request.user.is_authenticated:
            return False
        if 'Authorization' in request.headers and request.headers['Authorization'].startswith('Token '):
            from rest_framework.authtoken.models import Token
            try:
                token_key = request.headers['Authorization'].split(' ')[1]
                token = Token.objects.get(key=token_key)
                request.user = token.user  # Аутентифицируем пользователя по токену
                return True
            except (Token.DoesNotExist, IndexError):
                return False
        elif request.user.is_staff or request.user.is_superuser:
            return True
        # Проверка активного сотрудника
        try:
            return request.user.employee.is_active
        except AttributeError:
            return False  # Если у пользователя нет связанного Employee

        raise PermissionDenied(detail=self.message)  # Если ни одно условие не прошло

    def has_object_permission(self, request, view, obj):
        # Полный доступ для админов
        if request.user.is_staff or request.user.is_superuser:
            return True

        # Сотрудник может видеть только свой NetworkNode
        try:
            return obj == request.user.employee.network_node
        except AttributeError:
            return False
