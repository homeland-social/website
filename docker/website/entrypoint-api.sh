#!/bin/sh

DJANGO_DB_HOST=${DJANGO_DB_HOST:-db}
DJANGO_DB_PORT=${DJANGO_DB_PORT:-5432}

if [ ! -z "${DJANGO_DEBUG}" ]; then
    RELOAD=" --reload"
fi

if [ -z "${DJANGO_HOST}" ]; then
    DJANGO_HOST=localhost
fi

if [ -z "${DJANGO_PORT}" ]; then
    DJANGO_PORT=8000
fi

ARGS="--host=${DJANGO_HOST} --port=${DJANGO_PORT}${RELOAD}"

/wait-for ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}
uvicorn back.asgi:application ${ARGS}
