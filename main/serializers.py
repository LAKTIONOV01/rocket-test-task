from rest_framework import serializers
from .models import NetworkNode, Product, Employee

from django.contrib.auth.models import User


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)


class NetworkNodeSerializer(serializers.ModelSerializer):
    products = ProductSerializer(many=True, read_only=True)
    supplier = serializers.SlugRelatedField(slug_field='name', queryset=NetworkNode.objects.all(), required=False)

    class Meta:
        model = NetworkNode
        fields = '__all__'
        read_only_fields = ('created_at', 'level')

    def validate_debt(self, value):
        if self.instance and 'debt' in self.initial_data:
            raise serializers.ValidationError("Обновление задолженности через API запрещено")
        return value


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = '__all__'