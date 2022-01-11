FROM python:3-alpine AS python

ADD ./back /app
ADD ./docker/website/entrypoint-api.sh /entrypoint.sh

RUN wget https://raw.githubusercontent.com/eficode/wait-for/master/wait-for
RUN chmod +x /wait-for
RUN chmod +x /entrypoint.sh

# https://stackoverflow.com/questions/52894632/cannot-install-pycosat-on-alpine-during-dockerizing
WORKDIR /app
RUN apk add --no-cache git postgresql-client postgresql-dev gcc \
                       linux-headers musl-dev zlib zlib-dev libffi-dev && \
    echo "#include <unistd.h>" > /usr/include/sys/unistd.h && \
    pip3 install pipenv && \
    pipenv install --system && \
    apk del git gcc linux-headers postgresql-dev musl-dev zlib-dev libffi-dev

ENTRYPOINT [ "/entrypoint.sh" ]


FROM python AS celery

ADD ./docker/website/entrypoint-celery.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


FROM python AS beat

ADD ./docker/website/entrypoint-beat.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


FROM python AS migrate

ADD ./docker/website/entrypoint-migrate.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh


FROM python AS python-build

RUN python3 manage.py collectstatic --noinput


FROM node:17-alpine AS node

# For webpack:
# https://github.com/webpack/webpack/issues/14532
ENV NODE_OPTIONS=--openssl-legacy-provider
ADD ./front /app

WORKDIR /app
RUN npm i

ENTRYPOINT [ "npm", "run", "dev" ]


FROM node AS node-build

RUN npm run build

FROM nginx:1.21-alpine AS static

COPY --from=node-build /app/dist/static /usr/share/nginx/html/static
COPY --from=node-build /app/dist/index.html /usr/share/nginx/html
COPY --from=python-build /app/dist/static /usr/share/nginx/html/static
