from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from django.utils import timezone
from django.core.exceptions import ValidationError
from datetime import datetime


class NetworkNode(models.Model):
    NODE_TYPES = (
        ('factory', 'Завод'),
        ('distributor', 'Дистрибьютор'),
        ('dealership', 'Дилерский центр'),
        ('retail', 'Крупная розничная сеть'),
        ('entrepreneur', 'Индивидуальный предприниматель'),
    )

    name = models.CharField(max_length=255, verbose_name='Название')
    node_type = models.CharField(max_length=20, choices=NODE_TYPES, verbose_name='Тип звена')
    email = models.EmailField(verbose_name='Электронная почта')
    country = models.CharField(max_length=100, verbose_name='Страна')
    city = models.CharField(max_length=100, verbose_name='Город')
    street = models.CharField(max_length=100, verbose_name='Улица')
    house_number = models.CharField(max_length=20, verbose_name='Номер дома')
    supplier = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True,
                                 verbose_name='Поставщик', related_name='children')
    debt = models.DecimalField(max_digits=12, decimal_places=2, default=0,
                               validators=[MinValueValidator(0)], verbose_name='Задолженность')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Время создания')
    level = models.IntegerField(default=0, verbose_name='Уровень иерархии')
    products = models.ManyToManyField(
        'Product',
        related_name='network_nodes',
        blank=True,
        verbose_name='Продукты'
    )

    def clean(self):
        if len(self.name) > 50:
            raise ValidationError({'name': 'Название не может быть длиннее 50 символов'})

    def save(self, *args, **kwargs):
        if self.supplier:
            self.level = self.supplier.level + 1
        else:
            self.level = 0
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_node_type_display()}: {self.name}"


class Product(models.Model):
    name = models.CharField(max_length=255, verbose_name='Название')
    model = models.CharField(max_length=255, verbose_name='Модель')
    release_date = models.DateField(verbose_name='Дата выхода на рынок')
    primary_network_node = models.ForeignKey(NetworkNode, on_delete=models.SET_NULL, null=True,
                                             blank=True,
                                             related_name='primary_products', verbose_name='Звено сети')

    def clean(self):
        if len(self.name) > 25:
            raise ValidationError({'name': 'Название продукта не может быть длиннее 25 символов'})
        if self.release_date > datetime.now().date():
            raise ValidationError({'release_date': 'Дата выхода не может быть в будущем'})

    class Meta:
        verbose_name = 'Продукт'
        verbose_name_plural = 'Продукты'

    def __str__(self):
        return f"{self.name} {self.model}"


class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name='Пользователь')
    network_node = models.ForeignKey(NetworkNode, on_delete=models.CASCADE,
                                     related_name='employees', verbose_name='Звено сети')
    is_active = models.BooleanField(default=True, verbose_name='Активный сотрудник')

    class Meta:
        verbose_name = 'Сотрудник'
        verbose_name_plural = 'Сотрудники'

    def __str__(self):
        return self.user.get_full_name() or self.user.username
