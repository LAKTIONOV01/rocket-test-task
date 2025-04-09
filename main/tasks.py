from decimal import Decimal

from celery import shared_task
from django.db import transaction
from .models import NetworkNode
import random
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def increase_debt_randomly():
    """
    Увеличивает задолженность на случайное число от 5 до 500
    для всех объектов сети, у которых есть поставщик
    """
    nodes = NetworkNode.objects.exclude(supplier=None)
    increment = Decimal(str(round(random.uniform(5, 500), 2)))

    updated_count = 0
    with transaction.atomic():
        for node in nodes:
            node.debt += increment
            node.save()
            updated_count += 1

    # # Отправка уведомления (опционально)
    # send_mail(
    #     'Увеличение задолженности',
    #     f'Задолженность увеличена на {increment} для {updated_count} объектов',
    #     settings.DEFAULT_FROM_EMAIL,
    #     ['finance@example.com'],
    #     fail_silently=True,
    # )

    return f"Increased debt by {increment} for {updated_count} nodes"


@shared_task
def decrease_debt_randomly():
    """
    Уменьшает задолженность на случайное число от 100 до 10 000
    для объектов с положительной задолженностью
    """
    nodes = NetworkNode.objects.exclude(supplier=None).filter(debt__gt=0)
    decrement = Decimal(str(round(random.uniform(100, 10000), 2)))

    updated_count = 0
    with transaction.atomic():
        for node in nodes:
            node.debt = max(Decimal('0'), node.debt - decrement)
            node.save()
            updated_count += 1


    return f"Decreased debt by {decrement} for {updated_count} nodes"


@shared_task
def async_clear_debt(node_ids):
    """
    Асинхронная очистка задолженности для списка объектов
    Используется при массовой очистке (>20 объектов)
    """
    nodes = NetworkNode.objects.filter(id__in=node_ids)
    cleared_count = nodes.count()

    with transaction.atomic():
        nodes.update(debt=0)


    return f"Cleared debt for {cleared_count} nodes"