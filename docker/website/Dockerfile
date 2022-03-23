FROM python:3-alpine AS python

ENV DJANGO_DEBUG=false \
    DJANGO_DB_HOST= \
    DJANGO_DB_USER= \
    DJANGO_DB_NAME= \
    DJANGO_DB_PASSWORD= \
    DJANGO_ALLOWED_HOSTS=.homeland-social.com,.homelandsocial.com \
    DJANGO_NAME_SERVERS=1.1.1.1,8.8.8.8 \
    DJANGO_SHARED_DOMAINS=homeland.social \
    AUTHLIB_INSECURE_TRANSPORT=false \
    AUTHLIB_JWK=/run/secrets/jwk \
    AUTHLIB_JWK_PUB=/run/secrets/jwk.pub \
    SSH_HOST_KEYS=/run/secrets/ssh_host_*_key.pub \
    CELERY_BROKER_URL=redis://redis:6379/0 \
    CELERY_BEAT_SCHEDULER=django_celery_beat.schedulers:DatabaseScheduler

ADD ./back /app
ADD ./docker/website/entrypoint.sh /entrypoint.sh

RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for
RUN chmod +x /wait-for
RUN chmod +x /entrypoint.sh

# https://stackoverflow.com/questions/52894632/cannot-install-pycosat-on-alpine-during-dockerizing
WORKDIR /app
RUN apk add --no-cache git postgresql-client postgresql-dev gcc mailcap \
                       linux-headers musl-dev zlib zlib-dev libffi-dev && \
    echo "#include <unistd.h>" > /usr/include/sys/unistd.h && \
    pip3 install pipenv && \
    pipenv install --system && \
    apk del git gcc linux-headers postgresql-dev musl-dev zlib-dev libffi-dev

ENTRYPOINT [ "/entrypoint.sh" ]


FROM python AS python-build

RUN apk add --no-cache git && \
    pipenv install --system --dev && \
    python3 manage.py collectstatic --noinput && \
    apk del git


FROM node:17-alpine AS node

# For webpack:
# https://github.com/webpack/webpack/issues/14532
ENV NODE_OPTIONS=--openssl-legacy-provider
ADD ./front /app

WORKDIR /app
RUN npm i


FROM node AS node-build

RUN npm run build

FROM python AS final

ENV UWSGI_STATIC=on

COPY --from=python-build /app/api/static /app/static/static
COPY --from=node-build /app/dist/assets /app/static/assets
COPY --from=node-build /app/dist/index.html* /app/static/
