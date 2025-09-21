import os
from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("config")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks(["materials", "users"])
app.conf.beat_schedule = {
    "block-inactive-users-daily": {
        "task": "users.tasks.check_inactive_users",
        "schedule": crontab(hour=0, minute=0),
    },
}
app.conf.task_default_queue = "celery"
app.conf.task_routes = {"materials.tasks.*": {"queue": "celery"}}
app.conf.worker_pool = "solo"
app.conf.broker_connection_retry_on_startup = True
