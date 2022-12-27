import os

from django.conf import settings

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings.local')

app = Celery(
    'macroplate',
    backend=settings.CELERY_BACKEND,
    broker=settings.CELERY_BROKER,
    # if this option is True - celery task will run like default functions,
    # not asynchronous
    # http://docs.celeryproject.org/en/latest/userguide/configuration.html#task-always-eager
    task_always_eager=not settings.USE_CELERY,
)

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

app.conf.beat_schedule = {
    # We start cleaning every week on Wednesdays, because historical users are
    # only active on Mondays, and we delete them on Wednesday to avoid problems
    # with timezones.
    'clear_customers_history': {
        'task': 'apps.macroplate.tasks.remove_old_history_customers',
        'schedule': crontab(
            minute='0',
            hour='12',
            day_of_week='wed',
        )
    },
}
