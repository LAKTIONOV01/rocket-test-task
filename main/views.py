from rest_framework import viewsets, generics, permissions, filters
from rest_framework.response import Response
from django.db.models import Avg
from .models import NetworkNode, Product, Employee
from .serializers import NetworkNodeSerializer, ProductSerializer, EmployeeSerializer
from django.contrib.auth.models import User
from django_filters.rest_framework import DjangoFilterBackend


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