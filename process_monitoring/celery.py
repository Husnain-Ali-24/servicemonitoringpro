import os
from celery import Celery
from celery.schedules import crontab
from datetime import timedelta
from celery.schedules import schedule

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
    'check-websites-dynamically': {
        'task': 'monitoring.tasks.check_website_status',
        'schedule': schedule(timedelta(seconds=60)),  # ✅ Runs every 1 minute
    },
}
