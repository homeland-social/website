import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'back.settings')

app = Celery('api')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()


def task(f):
    """
    Allows us to define some global parameters for app.task().
    """
    return app.task()(f)
