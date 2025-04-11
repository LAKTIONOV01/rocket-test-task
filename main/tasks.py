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
    with transaction.atomic():
        NetworkNode.objects.filter(id__in=node_ids).update(debt=0)
    return f"Cleared debt for {len(node_ids)} nodes"


from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
import qrcode
from io import BytesIO
import base64
from .models import NetworkNode
from .serializers import NetworkNodeContactSerializer


@shared_task
def generate_qr_code(node_data):
    """Генерация QR-кода с контактными данными"""
    contact_info = f"""
    Название: {node_data['name']}
    Тип: {node_data['node_type']}
    Email: {node_data['email']}
    Адрес: {node_data['country']}, {node_data['city']}, {node_data['street']}, {node_data['house_number']}
    Телефон: {node_data.get('phone', 'не указан')}
    """

    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(contact_info)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    buffer = BytesIO()
    img.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode()


@shared_task
def send_network_contact_email(node_id, recipient_email):
    """Отправка email с контактными данными и QR-кодом"""
    node = NetworkNode.objects.get(id=node_id)
    serializer = NetworkNodeContactSerializer(node)
    node_data = serializer.data
    node_data['node_type'] = node.get_node_type_display()  # Добавляем отображаемое имя типа

    # Генерация QR-кода
    qr_code_data = generate_qr_code(node_data)

    subject = f"Контактные данные: {node_data['name']}"

    # Подготовка HTML и текстового содержимого
    context = {
        'node': node_data,
        'qr_code': qr_code_data
    }

    html_content = render_to_string('emails/network_contact_email.html', context)

    text_content = f"""
    Контактные данные: {node_data['name']}
    Тип: {node_data['node_type']}
    Email: {node_data['email']}
    Адрес: {node_data['country']}, {node_data['city']}, {node_data['street']}, {node_data['house_number']}
    Телефон: {node_data.get('phone', 'не указан')}
    """

    # Создание и отправка письма
    email = EmailMultiAlternatives(
        subject,
        text_content,
        'fxckaccerman@gmail.com',  # Используйте DEFAULT_FROM_EMAIL
        [recipient_email]
    )
    email.attach_alternative(html_content, "text/html")

    # Прикрепляем QR-код как вложение
    email.attach(
        f"qr_contacts_{node_id}.png",
        base64.b64decode(qr_code_data),
        "image/png"
    )

    email.send()
    return f"Письмо с QR-кодом отправлено на {recipient_email}"

