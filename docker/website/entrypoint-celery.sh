#!/bin/sh

DJANGO_DB_HOST=${DJANGO_DB_HOST:-db}
DJANGO_DB_PORT=${DJANGO_DB_PORT:-5432}

/wait-for ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}
python manage.py celery