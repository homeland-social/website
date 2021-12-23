#!/bin/sh

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

/wait-for db:5432
uvicorn back.asgi:application ${ARGS}
