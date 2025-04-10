from rest_framework import viewsets, generics, permissions, filters
from django.db.models import Avg
from .models import NetworkNode, Product, Employee
from .serializers import NetworkNodeSerializer, ProductSerializer, EmployeeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import send_network_contact_email
from rest_framework.exceptions import ValidationError
from .permissions import IsAdminOrActiveEmployee


class IsActiveEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return Employee.objects.filter(user=request.user, is_active=True).exists()
        return False


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminOrActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country']
    search_fields = ['name', 'city']

    def update(self, request, *args, **kwargs):
        # Явная проверка на попытку изменить debt
        if 'debt' in request.data:
            raise ValidationError({"detail": "Изменение задолженности запрещено"})
        return super().update(request, *args, **kwargs)

    def get_queryset(self):
        queryset = super().get_queryset()

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(products__id=product_id)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.supplier:
            instance.level = instance.supplier.level + 1
            instance.save()

    @action(detail=True, methods=['post'])
    def send_contacts(self, request, pk=None):
        """Отправляет контактные данные с QR-кодом на email"""
        node = self.get_object()
        recipient_email = request.data.get('email', request.user.email)

        # Асинхронная отправка через Celery
        send_network_contact_email.delay(node.id, recipient_email)

        return Response({
            "status": "success",
            "message": f"Письмо с QR-кодом будет отправлено на {recipient_email}",
            "node_id": node.id
        })





class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsAdminOrActiveEmployee]


class DebtStatisticsView(generics.ListAPIView):
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminOrActiveEmployee]

    def get_queryset(self):
        avg_debt = NetworkNode.objects.aggregate(avg_debt=Avg('debt'))['avg_debt']
        return NetworkNode.objects.filter(debt__gt=avg_debt)
