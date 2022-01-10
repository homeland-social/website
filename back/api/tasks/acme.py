# https://github.com/certbot/certbot/blob/master/acme/examples/http01_example.py

from back.celery import task

from django.conf import settings

USER_AGENT = ''


@task
def obtain_cert(domain_id):
    pass
