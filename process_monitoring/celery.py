import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta

# Set Django settings for Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "process_monitoring.settings")

app = Celery("process_monitoring")

# Load configuration from Django settings
app.config_from_object("django.conf:settings", namespace="CELERY")

# Make sure Celery is using Redis
app.conf.broker_url = os.getenv("CELERY_BROKER_URL", "redis://redis:6379/0")

# Discover tasks in installed Django apps
app.autodiscover_tasks()

# Define periodic tasks using Celery Beat
app.conf.beat_schedule = {
    'check-websites-every-30-sec': {
        'task': 'monitoring.tasks.check_30_sec',
        'schedule': timedelta(seconds=30),
    },
    'check-websites-every-1-min': {
        'task': 'monitoring.tasks.check_1_min',
        'schedule': timedelta(minutes=1),
    },
    'check-websites-every-2-min': {
        'task': 'monitoring.tasks.check_2_min',
        'schedule': timedelta(minutes=2),
    },
    'check-websites-every-5-min': {
        'task': 'monitoring.tasks.check_5_min',
        'schedule': timedelta(minutes=5),
    },
}
