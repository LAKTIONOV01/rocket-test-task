from rest_framework import permissions

class IsAdminOrActiveEmployee(permissions.BasePermission):
    """
    Разрешает доступ только:
    - Суперпользователям (is_superuser=True)
    - Администраторам (is_staff=True)
    - Активным сотрудникам (is_active=True)
    """
    def has_permission(self, request, view):
        return bool(
            request.user and
            request.user.is_authenticated and
            (request.user.is_staff or request.user.is_active)
        )