#!/bin/sh

DJANGO_DB_HOST=${DJANGO_DB_HOST:-db}
DJANGO_DB_PORT=${DJANGO_DB_PORT:-5432}
DJANGO_HOST=${DJANGO_HOST:-0.0.0.0}
DJANGO_PORT=${DJANGO_PORT:-8000}

if [ ! -z "${DJANGO_DEBUG}" ]; then
    ARGS="${ARGS} --py-autoreload=1"
fi

/wait-for ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}

# NOTE: --enable-proxy-protocol does not seem to work.
uwsgi --enable-threads --http-socket=${DJANGO_HOST}:${DJANGO_PORT} \
      --uid=65534 --gid=65534 --manage-script-name --gevent 1000 --http-websockets \
      --mount /=back.wsgi:application ${ARGS}
