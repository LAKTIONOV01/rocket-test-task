import os
from celery import Celery
import datetime

from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rocket.settings')

app = Celery('rocket')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(['main'])

# Периодические задачи
app.conf.beat_schedule = {
    'increase-debt-every-3-hours': {
        'task': 'main.tasks.increase_debt_randomly',
        'schedule': crontab(minute=0, hour='*/3'),  # Каждые 3 часа
    },
    'decrease-debt-daily': {
        'task': 'main.tasks.decrease_debt_randomly',
        'schedule': crontab(minute=30, hour=6),  # Ежедневно в 6:30
    },
}
