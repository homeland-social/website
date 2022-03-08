#!/bin/sh

CMD=${@:-api}

DJANGO_DB_HOST=${DJANGO_DB_HOST:-db}
DJANGO_DB_PORT=${DJANGO_DB_PORT:-5432}

/wait-for ${DJANGO_DB_HOST}:${DJANGO_DB_PORT}

if [ "${CMD}" == "api" ]; then
    DJANGO_HOST=${DJANGO_HOST:-0.0.0.0}
    DJANGO_PORT=${DJANGO_PORT:-8000}

    if [ ! -z "${DJANGO_DEBUG}" ]; then
        ARGS="${ARGS} --py-autoreload=1"
    fi

    # NOTE: --enable-proxy-protocol does not seem to work.
    uwsgi --enable-threads --http-socket=${DJANGO_HOST}:${DJANGO_PORT} \
        --uid=65534 --gid=65534 --manage-script-name --gevent 1000 --http-websockets \
        --mount /=back.wsgi:application ${ARGS}

elif [ "${CMD}" == "beat" ]; then
    celery -A back beat -l info

elif [ "${CMD}" == "celery" ]; then
    python manage.py celery

elif [ "${CMD}" == "migrate" ]; then
    python3 manage.py migrate --noinput

elif [ "${CMD}" == "test" ]; then
    python3 manage.py test

else
    /bin/sh -c ${CMD}
fi