from rest_framework import viewsets, generics, permissions, filters
from django.db.models import Avg
from .models import NetworkNode, Product, Employee
from .serializers import NetworkNodeSerializer, ProductSerializer, EmployeeSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import send_network_contact_email


class IsActiveEmployee(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.user.is_authenticated:
            return Employee.objects.filter(user=request.user, is_active=True).exists()
        return False


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = NetworkNode.objects.all()
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['country']
    search_fields = ['name', 'city']

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

    # @action(detail=True, methods=['post'])
    # def send_contacts(self, request, pk=None):
    #     """
    #     Отправляет контактные данные объекта на email пользователя
    #     POST /api/network-nodes/1/send_contacts/
    #     {
    #         "email": "optional@example.com"  # Опционально
    #     }
    #     """
    #     node = self.get_object()
    #     recipient_email = request.data.get('email', request.user.email)
    #
    #     send_network_contact_email.delay(node.id, recipient_email)
    #
    #     return Response({
    #         "status": "success",
    #         "message": f"Контактные данные будут отправлены на {recipient_email}",
    #         "node_id": node.id
    #     })




class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    permission_classes = [IsActiveEmployee]


class DebtStatisticsView(generics.ListAPIView):
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsActiveEmployee]

    def get_queryset(self):
        avg_debt = NetworkNode.objects.aggregate(avg_debt=Avg('debt'))['avg_debt']
        return NetworkNode.objects.filter(debt__gt=avg_debt)
