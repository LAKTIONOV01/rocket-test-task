from rest_framework import viewsets, generics, filters
from django.db.models import Avg
from .models import NetworkNode, Product
from .serializers import NetworkNodeSerializer, ProductSerializer
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.decorators import action
from rest_framework.response import Response
from .tasks import send_network_contact_email
from rest_framework.exceptions import ValidationError
from .permissions import IsAdminOrActiveEmployee
from rest_framework import status
from .filters import NetworkNodeFilter
from .serializers import NetworkNodeForProductFilterSerializer


class NetworkNodeViewSet(viewsets.ModelViewSet):
    queryset = NetworkNode.objects.all().prefetch_related('products')
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminOrActiveEmployee]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_class = NetworkNodeFilter

    def get_queryset(self):
        queryset = super().get_queryset()

        # Фильтрация по продукту (если есть в запросе)
        if 'product' in self.request.query_params:
            queryset = queryset.prefetch_related('products', 'supplier')

        product_id = self.request.query_params.get('product')
        if product_id:
            queryset = queryset.filter(products__id=product_id).distinct()

        # Для обычных сотрудников - только их NetworkNode
        if not (self.request.user.is_staff or self.request.user.is_superuser):
            try:
                queryset = queryset.filter(id=self.request.user.employee.network_node.id)
            except AttributeError:
                queryset = queryset.none()  # Нет доступа, если нет employee

        return queryset

    def get_serializer_class(self):
        if 'product' in self.request.query_params:
            return NetworkNodeForProductFilterSerializer
        return super().get_serializer_class()

    def update(self, request, *args, **kwargs):
        # Явная проверка на попытку изменить debt
        if 'debt' in request.data:
            raise ValidationError({"detail": "Изменение задолженности запрещено"})
        return super().update(request, *args, **kwargs)

    def perform_create(self, serializer):
        instance = serializer.save()
        if instance.supplier:
            instance.level = instance.supplier.level + 1
            instance.save()

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Удаление выполнено успешно"},
            status=status.HTTP_200_OK
        )

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

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response(
            {"message": "Удаление выполнено успешно"},
            status=status.HTTP_200_OK
        )


class DebtStatisticsView(generics.ListAPIView):
    serializer_class = NetworkNodeSerializer
    permission_classes = [IsAdminOrActiveEmployee]

    def get_queryset(self):
        avg_debt = NetworkNode.objects.aggregate(avg_debt=Avg('debt'))['avg_debt']
        return NetworkNode.objects.filter(debt__gt=avg_debt)
