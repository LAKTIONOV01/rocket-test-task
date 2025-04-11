from rest_framework import serializers
from .models import NetworkNode, Product, Employee

from django.contrib.auth.models import User
from datetime import datetime


class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = '__all__'
        read_only_fields = ('id',)

    def validate_name(self, value):
        if len(value) > 25:
            raise serializers.ValidationError("Название продукта не может быть длиннее 25 символов")
        return value

    def validate_release_date(self, value):
        if value > datetime.now().date():
            raise serializers.ValidationError("Дата выхода продукта не может быть в будущем")
        return value


class ProductShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name']


class NetworkNodeForProductFilterSerializer(serializers.ModelSerializer):
    supplier_name = serializers.CharField(source='supplier.name', read_only=True)

    class Meta:
        model = NetworkNode
        fields = [
            'id',
            'name',
            'node_type',
            'supplier_name',
            'country',
            'city',
            'debt',
            'level',
            'created_at'
        ]
        read_only_fields = fields


class NetworkNodeSerializer(serializers.ModelSerializer):
    products = ProductShortSerializer(many=True, read_only=True)
    supplier = serializers.SlugRelatedField(slug_field='name', queryset=NetworkNode.objects.all(), required=False)

    class Meta:
        model = NetworkNode
        fields = '__all__'
        read_only_fields = ('created_at', 'level', 'debt')

    def validate_name(self, value):
        if len(value) > 50:
            raise serializers.ValidationError("Название объекта сети не может быть длиннее 50 символов")
        return value

        # Дополнительная валидация для всех данных

    def validate(self, data):
        if 'debt' in data and self.instance and data['debt'] != self.instance.debt:
            raise serializers.ValidationError({"debt": "Нельзя изменять задолженность через API"})
        return data


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name')


class EmployeeSerializer(serializers.ModelSerializer):
    user = UserSerializer()

    class Meta:
        model = Employee
        fields = '__all__'


class NetworkNodeContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = NetworkNode
        fields = ['id', 'name', 'email', 'country', 'city', 'street', 'house_number']
